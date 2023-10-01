from typing import Any
import subprocess
import copy

from .command import Command, CommitResult
from .utils import *


def Run(cmd: str | Command, *args: str, **kwargs: Any) -> CommitResult:
    """Executes the command with the arguments.

    Returns:
      a CommitResult containing retcode, stdout, stderr and the elapsed time in seconds.

    Keyword arguments:
    * strict: bool=False
      If true, non-zero return status or timeouts will be notified by to a
      CalledProcessError exception or TimeoutExpired exception.  Otherwise it is silently stored in the
      CommitResult.
    * timeout: int|str=None
      Timeout in seconds, or suffixed with [smh].
    * stdin: str=None
      Supplied stdin input.
    """
    if isinstance(cmd, str):
        cmd = Command(cmd)
    cmd = copy.deepcopy(cmd)
    return cmd.commit(*args, **kwargs)


def Cap(cmd: str | Command, *args: str, **kwargs: Any) -> bytes | str:
    """Executes the command with the arguments and captures the output.

    Returns:
      a str containing the stdout contents.
      By default strips the output.

    Keyword arguments:
    * strip: bool=True
    * for more check Run().
    """
    CAP_KEYS = ["strip"]
    strip = kwargs.get("strip", True)
    kwargs = dict(kv for kv in kwargs.items() if kv[0] not in CAP_KEYS)
    res = Run(cmd, *args, **{"stdout": subprocess.PIPE} | kwargs)
    if strip:
        return res.stdout.strip()
    else:
        return res.stdout
