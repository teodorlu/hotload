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


def _listfiles(folder, ext=""):
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


class PythonModule(Runnable):
    def __init__(self, module):
        assert isinstance(module, ModuleType), (
            "PythonModule requires a module handle as input."
            "Use PythonModule.from_module_name to construct a PythonModule from"
            " a module name (string)"
        )
        self.module = module

    @staticmethod
    def from_module_name(module_name):
        module = importlib.import_module(module_name)
        return PythonModule(module)

    def run(self):
        try:
            _reload_module(self.module)
            print("Successfully reloaded {} @ {}".format(self.module.__name__, datetime.datetime.now()))
        except:
            traceback.print_exc()
            pass
    pass


class ClearTerminal(Runnable):
    def run(self):
        os.system('cls' if os.name=='nt' else 'clear')


def runsteps(steps):
    for step in steps:
        step.run()


def hotload(watch, steps):
    # TODO reload
    runsteps(steps)
    pass


def hotload_single_iter(watch, steps):
    runsteps(steps)

