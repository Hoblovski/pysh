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
    * capture: bool=False
      Whether to capture stdout AND stderr.
      Precedence is lower than redirection.
    """
    (suppress, capture) = multipop_dict(kwargs, suppress=False, capture=False)
    if isinstance(cmd, str):
        cmd = Command(cmd)
    cmd = copy.deepcopy(cmd)
    try:
        if capture:
            kwargs = {"o": subprocess.PIPE, "e": subprocess.PIPE} | kwargs
        return cmd.commit(*args, **kwargs)
    except Exception as e:
        if not suppress:
            raise
        return CommitResult(CommitResKind.CRITICAL, None, "", "", None)


def Cap(cmd: str | Command, *args: str, **kwargs: Any) -> str:
    """Executes the command with the arguments and captures stdout.
    Different from the capture kwargs, which additionally captures stderr.

    Returns:
      a str containing the stdout contents.
      By default strips the output.

    Keyword arguments:
    * strip: bool=True
    * for more check Run().
    * capture: NOT SUPPORTED

    Note that if you already redirect stdout in kwargs, the captured output
    might be lost.
    """
    (strip,) = multipop_dict(kwargs, strip=True)
    # kwargs takes precedence so that Cap works with redirects
    res = Run(cmd, *args, **{"o": subprocess.PIPE} | kwargs)
    stdout = res.stdout
    if isinstance(stdout, bytes):
        raise ValueError(f"You can only capture text stdout with Cap(), but got bytes.")
    if strip:
        return stdout.strip()
    else:
        return stdout
