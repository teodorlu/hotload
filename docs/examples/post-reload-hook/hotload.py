from __future__ import print_function

import datetime
import importlib
import os
import time
import traceback

from abc import abstractmethod
from pprint import pprint
from types import ModuleType


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
    return {
        path: _file_changed(path)
        for path in filepaths
    }


def listfiles(folder, ext=""):
    fs = list()
    for root, dirs, files in os.walk(folder):
        fs.extend(
            os.path.join(root, f) for f in files
            if f.endswith(ext)
        )
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
    def __init__(self, module, post_reload_hook=None):
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
        print("Successfully reloaded {} @ {}".format(self.module.__name__, datetime.datetime.now()))
    pass


class ClearTerminal(Runnable):
    def run(self):
        os.system('cls' if os.name=='nt' else 'clear')


def hotload(watch, steps, waittime_ms=1.0/144):
    """Hotload that code!"""

    # Avoid duplicates in the recurring check
    watchfiles = set()
    for targets in watch:
        for path in targets:
            watchfiles.add(path)

    # Take note of when files were last changed before we start reloading
    last_changed = _all_file_changes(watchfiles)
    for step in steps:
        try:
            step.run()
        except KeyboardInterrupt:
            print("Interrupt received, stopping hotload")
            return
        except:
            print("Error running {}".format(step))
            traceback.print_exc()

    # Begin the loop! Each Runner is responsible for handling its own exceptions.
    while True:
        new_changed = _all_file_changes(watchfiles)
        if last_changed == new_changed:
            time.sleep(waittime_ms)
        else:
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
            pass
    pass
