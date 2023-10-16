# PySh: Palliate you Shell headaches
[![Test status](https://github.com/hoblovski/pysh/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/hoblovski/pysh/actions/workflows/test.yml)

Readable, safe and powerful shell scripting in Python.

Works on Python 3.11.

## MOTIVATION
The old good shell scripting has a bad name for readability, portability and
error handling.  You can accidentally wipe out a file without noticing it.
Every time you have to check the manual for the syntax of arrays and
associative arrays.  The procedures compose badly. Missing arguments are
defaulted to empty.  You do not know which commands mutate the disk and system
configurations and which do not. Debugging bash scripts is pain.

## OVERVIEW
PySh is a python library that allows users to write bash scripts in python.
Scripts are more readable. Errors are explicit. Parellelism is out-of-the-box.
PySh is well-documented, well-tested and type-annotated.

PySh is 100% compatible with Python and Python libraries. Everything in PySh is
also valid Python, because PySh is simply a shallow embedding DSL in Python.

## SETUP
[WIP: upload to pypi]

Clone the repo and install manually
```
python3 -m pip install -r requirements.txt
python3 -m pip install .
```


# USAGE
For real scripts, check examples/ and tests/.

Basic usage:
```python
#!/usr/bin/env python3
from pysh import *

# Run a command
Run(echo_, "Hello world")  # prints: Hello world

# Command alias
greet = echo_("Hello world")  # not executed until Run
Run(greet)

# Extending a command
greet_tom = greet("tom")
Run(greet_tom)  # prints: Hello World tom

# I/O redirection
Run(greet, o="greeting.txt")  # same as `echo "Hello world" >greeting.txt`
Run(sed, "s/Hello/Hola/", i="greeting.txt")  # prints: Hola world
lserr = ls_("-1", ".", "/NONEXIST")  # a command with both stdout and stderr
Run(lserr, o="ls.txt", eo=1)  # Same as `ls -1 . NONEXIST >ls.txt 2>&1`

# Creating a command from scratch
count_chars = Command("wc", "-c")

# Using pipes
Run(greet | sed("s/ll/l/") | count_chars)  # prints: 11 (including \n)

# Builtin time
Run("seq", "10000000", eo=0).elapsed  # returns: 0.064 (seconds)

# Capture stdout, just like $(cmd)
res = Cap(lserr)  # stderr not captured
print(res)  # prints: .:\nexamples\ngreeting.txt\n...

# Capture both stdout and stderr
res = Run(lserr, capture=True)  # prints: nothing
print(res.stdout, res.stderr)

# Session-based cd
with ChDir("/"):
    Run(ls_)  # lists root directory
Run(ls_)  # lists current directory

# Check return vlaues
if not Run(lserr, oe=0):
    print("lserr failed")  # prints: lserr failed
if Run(ls_, oe=0):
    print("ls succeeded")  # prints: ls succeeded
```

# TODO
* upload to pypi with a better name maybe Psyche
* a better way to help indicate the CWD
* serialize command into string representation
* fix TODO in sources
* exporting environment variables
* control operator `&&`, `||`, `;`
* command groups and subshells
* restricted shell
* parallelism similar to GNU parallel, maybe use async await
* builtin xargs maybe?
* quick pathlib.Path conversion to save keystrokes
* binary I/O with Run.retval

# For developers
To allow tests to find PySh while developing it, execute
```
$ python3 -m pip install -e .
```

PySh uses static types to improve realiability.
After any modifications, you should type-check the sources before executing them:
```
$ python3 -m mypy src tests
```

When you are contributing, make sure the code is well formatted
```
$ python3 -m black src tests
```

