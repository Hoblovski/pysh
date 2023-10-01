from typing import Any
import subprocess
import copy

from .command import Command, CommitResult, CommitResKind
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
    * suppress: bool=False
      ONLY ENABLE WHEN YOU KNOW WHAT YOU ARE DOING!
      If true, suppress all python exceptions raised by the command.
      Can cause bugs to go undetected, like mistyped commands.
    * timeout: int|str=None
      Timeout in seconds, or suffixed with [smh].
    * input: str=None
      Supplied stdin input.
    """
    (suppress,) = multipop_dict(kwargs, suppress=False)
    if isinstance(cmd, str):
        cmd = Command(cmd)
    cmd = copy.deepcopy(cmd)
    try:
        return cmd.commit(*args, **kwargs)
    except Exception as e:
        if not suppress:
            raise
        return CommitResult(CommitResKind.CRITICAL, None, "", "", None)


def Cap(cmd: str | Command, *args: str, **kwargs: Any) -> bytes | str:
    """Executes the command with the arguments and captures the output.

    Returns:
      a str containing the stdout contents.
      By default strips the output.

    Keyword arguments:
    * strip: bool=True
    * for more check Run().
    """
    (strip,) = multipop_dict(kwargs, strip=True)
    # kwargs takes precedence so that Cap works with redirects
    res = Run(cmd, *args, **{"o": subprocess.PIPE} | kwargs)
    if strip:
        return res.stdout.strip()
    else:
        return res.stdout
