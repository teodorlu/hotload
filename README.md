# Python: hotloaded

<!-- Consider photoshopping in a matrix reloaded picture here! -->

`hotload` enables exploratory programming with Python by providing a super-fast
feedback loop and continuous program state. `hotload` differs from other
reloaders with its focus on

- Minimal dependencies
- Simple execution model.

## Getting started with hotload

Hotload is distributed as a single file.

1. Create `lib.py` and `load.py` in a new folder
2. Copy [hotload.py][4] in there as well.

[4]: ./hotload.py

Our task is to develop `lib.py`. We're going to do this by creating a really
fast feedback loop, where saves trigger re-runs.

```python
# In lib.py

x = 3
y = 4

print(x*x + y*y)
```

To hotload `lib.py`, we're going to use `load.py` as a load script. This
script sets up and runs `hotload`. We'll use this start:

```python
# In launch.py

import hotload

hotload.hotload(
    watch=[
        hotload.listfiles(".", ext=".py")
    ],
    steps=[
        hotload.ClearTerminal(),                               # (1) 
        hotload.ReloadedPythonModule.from_module_name("lib"),  # (2)
    ]
)

# (1) hotload.ClearTerminal() ensures a "dashboard"-like experience when we work, so
#     that the terminal doesn't keep scrolling down.

# (2) then we set up a reloaded python module.
```

Now, use it! Run the launch script with

```
$ python launch.py
```

... and edit lib.py and save! You should trigger a reload each time you save.

## Supported platforms

`hotload` avoids external dependencies, and aims to be portable. Why support
Python 2? Because it's when interacting with old, stale systems with poor
documentation that hotloading really shines.

`hotload` has been tested on the following systems:

- system-installed Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Windows 10
- Anaconda Python 2.7.15 on Windows 10
- Abaqus Python 2.7.4

## Advanced usage

You might want to have a look here after getting a feel for the reloading.

### Exceptions and interrupts

The balance between liveness and security is fragile. Thus, it's recommended to
understand the exception model of hotload.

1. `C-c` (Control-c) interrupts the reload loop
2. For all other exceptions, the stacktrace is printed and the reload loop
   continues.

### Why doesn't the modules i use _from_ lib reload?

The following setup won't reload `mymath.py`:

```python
# in lib.py

import mymath

print(mymath.f(1,2))
```

```python
# in mymath.py

def f(x):
    return x*x + y*y
```

To trigger reloads in `mymath.py` from the `lib.py` entry point, we need a
manual reload. Reloading differs between Python 2 and 3.

```python
# In lib.py, Python 3

from importlib import reload

import mymath
reload(mymath)

print(mymath.f(2,3))
```

A design note. The first version of this library tried to infer what modules it
would have to reload. It maintained a list of all the modules it had previously
reloaded, and watched those for files. Lots of automation. Lots of complexity.
In the end, I didn't find it useful at all. Instead, I add in reloads in the
modules I'm developing at the top like this. The advantage? It's all dynamic --
I don't have to restart `hotload` -- it can just keep on runnning. If you've
chosen to watch a folder, each file change will trigger a reload to the
top-level entry point.

### Calling a specific function in a module after reload

Just developing modules by having a reload "be your test" works fine for small
modules, and is quite nice to work with. However, I've found it problematic for
larger systems. Then I'd like to create an init function in the bottom of the
file instead, and call the init function from hotload.

To use this, you can extend `hotload.ReloadedPythonModule` and override
`pre_reload_hook` (for cleanup) or `post_reload_hook` (for initialization).

This allows you to let the your reloadable application code stay clean and nice,
and you can provide different configurations for running different parts of your
code.

### How do I persist state across reloads?

Usage cases:

- Keep a connection to an external system open under reloads
- Avoid having to re-run time-consuming external calls on each reload

You can use NameError to trigger the computation in the first place:

```python
# in mymath.py

import time

def expensive_computation():
    # ...
    time.sleep(5)
    42

try:
    constant = constant
except NameError:
    constant = expensive_computation
```

This will trigger `expensive_computation()` on the first run, and cache the
result on the next reload. Why? Because `reload` doesn't flush the module's
namespace. It still has access to everything that was there before! Which can be
neat ...
   
## References

- [entr][1] provides this workflow as a command-line, language-agnostic tool. I
  use entr all the time on linux. Limitations: you have to hop out of your
  Python context, and you'll have to install it on a target environment which
  supports it.
- Test runners for Python. Some test runners provide autotest functionality.
  They build in file watching like what I've used here, and can automatically
  provide you with test output as you develop your application. Just hit save,
  and see a new (and greener) list of all the tests that fail and pass!
- Other Python reloaders like [hoh/reloadr][2].

[1]: http://eradman.com/entrproject/
[2]: https://github.com/hoh/reloadr

## FAQ

- **Q**: Does hotload use polling?
- **A**: Yes. That means it asks the OS whether all watched files have changed
  each iteration (by default 144 iterations per second). Using polling is
  simple, and works across systems. If you need lower response times or less
  system load, you might want to use something like [inotify][3] on Linux.
  Search for existing Python libraries! Note that these are going to be more
  complex than hotload.
  
[3]: http://man7.org/linux/man-pages/man7/inotify.7.html
