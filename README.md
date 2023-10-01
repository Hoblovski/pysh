# PySh: Palliate you Shell headaches
[![Test status](https://github.com/hoblovski/pysh/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/hoblovski/pysh/actions/workflows/test.yml)

Less pain bash scripting: safer and more portable.

Works on Python 3.11.

## OVERVIEW
PyShell is a python library that allows users to write bash scripts in python,
with almost the same syntax as in a shell script.

The old good shell scripting has a bad name for readability, portability and
error handling.  You can accidentally wipe out a file without noticing it.
Every time you have to check the manual for the syntax for array and
associative array manipulation.  The procedures compose badly.  Debugging bash
scripts is pain.

## EXAMPLES
Check examples/, and also tests/.

## SETUP
* Install all requirements `python3 -m pip install -r requirements.txt`

## USAGE
* PySh scripts

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

# REFERENCE
[WIP]
## FEATURES
1. REDIRECTION
  - `cmd <t.txt >/dev/null 2>&1` becomes `cmd(i='t.txt', o=None, eo=1)`

2. PIPE
  - `cmd | cmd`

3. [TODO] Pain-free parallelism

4. [TODO] Expansion
  - Command Substitution: `$(cmd)`

5. [TODO] Bultins
  - `export`
  - `&&`, `||` and `;`

Support:
```
if grep -q x:
popd?pushd?
restricted shell for safety?
quick conversion to Path to avoid all pathlib.Path gibberish
```

# TODO
* fix TODO in sources
* fix examples/
* better motivating example in README
