import contextlib
import os
from pathlib import Path


@contextlib.contextmanager
def ChDir(path: str | Path):
    """Session-based cd.
    USAGE
        with ChDir(".."):
            Run("ls")

    Still this modifies the system-wide CWD.
    Better is to individually supply cwd parameters to subprocess."""
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)
