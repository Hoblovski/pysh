#!/usr/bin/env python3
# bash source -> python import
import sys
from pysh import *
from pathlib import Path

# missing parameter no longer do undetected
try:
    argv1 = sys.argv[1]
except IndexError:
    argv1 = ""

if argv1 == "version":
    # Use print normally, but we also have echo_ for the stubborn.
    Run(echo_, "Example version: 0.1")
    exit(0)

else:
    # Builtin elapsed time accounting
    print(Run("seq", "100000000", o=None).elapsed)

    # Session-based cd
    # Type-safe object oriented pathlib.Path
    with ChDir(Path(sys.argv[0]).parent.parent):
        # Capture command output $(cmd)
        # Pipelining
        files = Cap(find(".") | sort | head("-n", "10"))
        # The str->list convertsion made explicit
        for f in files.splitlines():
            print(f"Got file {f}")
        tf = Cap("tempfile")
        print(f"Files written to {tf}")
        # Modern file I/O.
        Path(tf).write_text(files)
        f = input("Check for existence of: (input)")
        # Check command status with if
        # Redirect output with kwargs
        if Run(grep, f"{f}$", tf, eo=0):
            print("Present")
        else:
            print("Absent")
