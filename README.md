# PyShell
[![Test status](https://github.com/hoblovski/pysh/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/hoblovski/pysh/actions/workflows/test.yml)

Less pain bash scripting: safer and more portable.

Works on Python 3.11.

## Overview
PyShell is a python library that allows users to write bash scripts in python,
with almost the same syntax as in a shell script.

The old good shell scripting has a bad name for readability, portability and
error handling.  You can accidentally wipe out a file without noticing it.

## EXAMPLES
Check examples/, and also tests/.

# REFERENCE
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
