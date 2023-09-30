# PyShell
Less pain bash scripting: safer and more portable.

## Overview
PyShell is a python library that allows users to write bash scripts in python,
with almost the same syntax as in a shell script.

The old good shell scripting has a bad name for readability, portability and
error handling.  You can accidentally wipe out a file without noticing it.

## EXAMPLE
Check examples.


# REFERENCE
## FEATURES
1. REDIRECTION
  - `>`, `>>`, `2>`, `<`
  - Special shorthand for `/dev/null` and `2>&1`

2. PIPE

3. Pain-free parallelism

4. Expansion
  - Command Substitution: `$(cmd)`

5. Bultins
  - `export`
  - `&&`, `||` and `;`

## Idiom Change
  - `source` -> `import`

Support:
```
if grep -q x:
popd?pushd?
restricted shell for safety?
quick conversion to Path to avoid all pathlib.Path gibberish
```
