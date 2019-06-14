# Hotload your Python like there's no tomorrow!

`hotload` enables exploratory programming with Python by providing a super-fast
feedback loop and continuous program state. `hotload` differs from other
reloaders with its focus on

- Minimal dependencies
- Simple execution model.

## Installation

1. Copy `hotload.py` from this repository into your project
2. You're done!

## Usage

With `hotload.py` in our working directory, we're going to need (a) our
hotloading configuration and (b) the file we're going to work with. That leaves
us with:

- `hotload.py` is just copied from here.
- `load.py` is your configuration for hotload. Having this as a Python file
  allows you to configure hotload to your liking.
- `mylib.py` is the file you're working on. This is the file we're going to
  hotload.

## Supported platforms

`hotload` avoids external dependencies (other than the Python library), and aims
to be portable. Why support Python 2? Because it's when interacting with old,
slow systems hotloading really shines.

`hotload` has been tested on the following systems:

- system-installed Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Ubuntu 18.04
- Anaconda Python 3.7.3 on Windows 10
- Anaconda Python 2.7.15 on Windows 10
- Abaqus Python 2.7.4

## Other things you might interested in

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
