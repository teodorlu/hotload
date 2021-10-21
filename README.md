# Hotload your Python

`hotload` enables exploratory programming with Python by providing a super-fast
feedback loop and continuous program state.

## Why hotload?

Hotload lets you reload a single file, rather than rerunning your application.
That really makes a difference when your dependencies are heavy. When I'm
testing this script:

```python
# script_with_deps.py

import numpy as np
import pandas as pd
import altair as alt
import psycopg2

print("Done!")
```

`python script_with_deps.py` completes in 480 ms, whereas a `hotload` reload
completes in 4 ms. For big projects, this can allow you to stay focused, and
test your changes continuously. In addition, you don't have to switch out to a
terminal, a single control+s in the file you're developing is enough.

`hotload` is simple:

- No dependencies other than Python 2/3.
- Small: at ~200 lines, you can read it in a few minutes.

## Quick start with CLI (Linux / Mac)

Windows users: you'll currently have to use the Python API (next section). Sorry for that!

With the CLI, you'll be running hotload as a binary script. This is nice for
testing small things, and works as an alternative to calling `python` manually
on the command line each time you want to run the script.

1. Install the script. Download `hotload.py` manually and make it executable, or
   use this one-liner:

        curl https://raw.githubusercontent.com/teodorlu/hotload/master/install.sh | bash

2. Ensure that you have `~/.local/bin` on your path.

3. Create `hello.py`, and try `echo hello.py | hotload hello.py`

Make some changes to `hello.py`. Can you see it change?

Note: Windows support for the CLI would be nice, but I rarely (never) use the
Windows command line to run scripts. If you're using Windows Susbsystem for
Linux, the install instructions should work just fine from a bash shell. Ideas /
discussion / PRs for proper Windows CLI support is interesting, though.

## Using the Python API (Linux / Mac / Windows)

With the Python API, you'll have more flexibility in how you run Hotload. You
may configure what files should be watched, whether you want the screen to
refresh, and you may load multiple modules.

Hotload is distributed as a single file

1. Create `lib.py` and `load.py` in a new folder
2. Copy [hotload.py][4] in there as well.

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

... and edit lib.py and save! Each save triggers a new reload.

## Supported platforms

`hotload` avoids external dependencies, and aims to be portable. Why support
Python 2? Because it's when interacting with old, stale systems with poor
documentation that hotloading really shines.

`hotload` has been tested on the following systems:

- Source-built Python 3.8.1 on Ubuntu 18.04
- system-installed Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Windows 10
- Anaconda Python 2.7.15 on Windows 10
- Abaqus Python 2.7.4 on Windows 10

If any of these platforms break, please report the bug in an issue. If you're on
a different platform and something breaks, please consider making a feature
request in an issue.

## Advanced usage

Did you get the reloaded experience? Good! Would you like some more? Then,
please read on! This is going to cover some limitations with naïve reloading,
and how we can overcome them.

### Exceptions and interrupts

The balance between liveness and reliability is important. Therefore, it's recommended to
understand the exception model of hotload.

1. `C-c` (Control-c) interrupts the reload loop
2. For all other exceptions, the stacktrace is printed and the reload loop
   continues.

### Why aren't recursive dependencies reloaded?

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

See the [post-reload-hook][5] example for more details!

### How do I persist state across reloads?

Usage cases:

- Keep a connection to an external system open under reloads
- Avoid having to re-run time-consuming external calls on each reload

You can use NameError to trigger the computation in the first place:

```python
# in lib.py

import time

def expensive_computation():
    # ...
    time.sleep(5)
    return 42

try:
    constant = constant
except NameError:
    constant = expensive_computation()
```

This will trigger `expensive_computation()` on the first run, and cache the
result on the next reload. Why? Because `reload` doesn't flush the module's
namespace. It still has access to everything that was there before! Which can be
neat ...

## Inspiration

- Bruce Hauman's [Figwheel][6] revolutionized web development by hotloading new
  code into a running JavaScript environment. Thanks!
   
## Future work

**Hotload's command line interface may need some work**. In its current form,
it's quite limited. We could try to go for multiple arguments:

```
find . | grep ".py" | hotload.py --clear-terminal --hotload script --run echo "That's a reload!"
```

**It might be useful to run hotload in the background**. Why? Because then we
could interact with a hotloaded Python REPL that (at all times) is aware of our
code.

**Tests** might be nice. To be able to ensure that there's no primitive errors
across platforms. Challenge: hotload typically operates on the "outer" layer of
a code base, so we'd have to build an outer-outer layer.

## Other options

- [Jupyter Notebooks][7] enable a similar workflow, where you import your
  dependencies _once_ and stay in-process afterwards. Notebooks are a good
  option when you don't want to consider your script as a whole.
- [entr][1] provides this workflow as a command-line, language-agnostic tool. I
  use entr all the time on Linux. Limitations: you have to hop out of your
  Python context, and you'll have to install it on a target environment which
  supports it.
- Test runners for Python. You can use hotload with a test runner, and have your
  `lib.py` run the test runner, thereby avoid having to restart the Python
  interpreter. Or you might have a test runner with a built in reloader; in
  which case you might not need this.
- Other Python reloaders like [hoh/reloadr][2].

## FAQ

- **Q**: Does hotload use polling?
- **A**: Yes. That means it asks the OS whether all watched files have changed
  each iteration (by default 144 iterations per second). Using polling is
  simple, and works across systems. If you need lower response times or less
  system load, you might want to use something like [inotify][3] on Linux.
  Search for existing Python libraries! Note that these are going to be more
  complex than hotload.
  
[1]: http://eradman.com/entrproject/
[2]: https://github.com/hoh/reloadr
[3]: http://man7.org/linux/man-pages/man7/inotify.7.html
[4]: ./hotload.py
[5]: ./docs/examples/post-reload-hook/
[6]: https://figwheel.org/
[7]: https://jupyterlab.readthedocs.io/en/stable/
