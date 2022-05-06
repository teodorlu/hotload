#!/usr/bin/env python3

from __future__ import print_function

import datetime
import importlib
import os
import re
import sys
import time
import traceback

from abc import abstractmethod
from pprint import pprint
from types import FunctionType, ModuleType


# Turn on to see how long each reload takes.
TIME_RELOADS = False


################################################################################
# UTILITY FUNCTIONS


def _reload_module(module):
    """Reload a module from Python 2 or 3"""
    try:
        importlib.reload(module)
    except AttributeError:
        # Fallback for Python 2
        reload(module)


def _file_changed(f):
    """Read os metadata for last modification of file at `f`

    Tested on Unix and Windows. More details in the standard library[1].

    [1]: https://docs.python.org/3/library/stat.html#stat.ST_CTIME

    """
    return os.stat(f).st_mtime


def _all_file_changes(filepaths):
    return {path: _file_changed(path) for path in filepaths}


def listfiles(folder, ext=""):
    fs = list()
    for root, dirs, files in os.walk(folder):
        fs.extend(os.path.join(root, f) for f in files if f.endswith(ext))
    return fs


################################################################################
# RUNNABLE
#
# Runnables can be run. That's it! A few runnables are included for running
# some compile-time Python, running a system command, running a dynamically
# reloaded Python module.
#
# Consideration: should I ensure that I can pass state between reloads? Or
# should I handle that internally? Perhaps simplest just to handle locally.


class Runnable(object):
    @abstractmethod
    def run(self):
        pass

    pass


class PythonHandle(Runnable):
    def __init__(self, code):
        self.code = code

    def run(self):
        self.code()

    pass


class Command(Runnable):
    def __init__(self, command):
        self.command = command

    def run(self):
        os.system(self.command)

    pass


class ReloadedPythonModule(Runnable):
    def __init__(self, module):
        assert isinstance(module, ModuleType), (
            "ReloadedPythonModule requires a module handle as input."
            "Use ReloadedPythonModule.from_module_name to construct a PythonModule from"
            " a module name (string)"
        )
        self.module = module

    @classmethod
    def from_module_name(cls, module_name):
        module = importlib.import_module(module_name)
        return cls(module)

    def pre_reload_hook(self, _):
        pass

    def post_reload_hook(self, _):
        pass

    def run(self):
        self.pre_reload_hook(self.module)
        _reload_module(self.module)
        self.post_reload_hook(self.module)
        print(
            "Successfully reloaded {} @ {}".format(
                self.module.__name__, datetime.datetime.now()
            )
        )

    def function(self, function_name):
        function = self.module.__dict__[function_name]
        assert isinstance(function, FunctionType)
        return function

    pass


class ClearTerminal(Runnable):
    def run(self):
        os.system("cls" if os.name == "nt" else "clear")


def hotload(watch, steps, waittime_ms=1.0 / 144):
    """Hotload that code!"""

    # Avoid duplicates in the recurring check
    watchfiles = set()
    for targets in watch:
        for path in targets:
            watchfiles.add(path)

    # Take note of when files were last changed before we start reloading
    last_changed = None

    # Begin the loop! Each Runner is responsible for handling its own exceptions.
    while True:
        new_changed = _all_file_changes(watchfiles)
        if last_changed == new_changed:
            time.sleep(waittime_ms)
        else:
            reload_begin_ms = time.time() * 1000
            last_changed = new_changed
            try:
                for step in steps:
                    try:
                        step.run()
                    except KeyboardInterrupt:
                        raise
                    except:
                        print("Error running {}".format(step))
                        traceback.print_exc()
            except KeyboardInterrupt:
                print("Interrupt received, stopping hotload")
                return
            reload_done_ms = time.time() * 1000
            if TIME_RELOADS:
                print(f"Reloaded in {reload_done_ms - reload_begin_ms} ms")
            pass
    pass


def main():
    USAGE = """Usage: hotload SCRIPT
Hotload python script when files on standard input change

Example usage:

    find . -name '*.py' | hotload init.py

.py extension for script may be omitted.
"""
    print("Running hotload ...")
    sys.path.append(".")

    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    entrypoint = None

    for i, cliarg in enumerate(sys.argv):
        # Look for CLI options
        if i < 2:
            # Must be "hotload" and "script"
            continue
        if cliarg == "--entrypoint":
            try:
                entrypoint = sys.argv[i + 1]
            except IndexError:
                print("LOL")

    print("Nothing happening? Remember to pass watch files on stdin.")
    print("Example: ls *py | hotload hello.py")
    print()
    print("  ls *py | hotload hello.py")

    watchfiles = [f.strip() for f in sys.stdin.readlines()]

    if not watchfiles:
        print("Error: no watch files specified.")
        print(USAGE)
        sys.exit(1)

    init_module = re.sub(r"\.py", "", sys.argv[1])

    os.environ["HOTLOAD_RUNNING"] = "HOTLOAD_RUNNING"

    reloaded_module = ReloadedPythonModule.from_module_name(init_module)
    if entrypoint:
        reloaded_module.post_reload_hook = lambda _: reloaded_module.function(entrypoint)()

    conf = {
        "watch": [watchfiles],
        "steps": [ClearTerminal(), reloaded_module],
    }

    hotload(**conf)

    pass


if __name__ == "__main__":
    main()
