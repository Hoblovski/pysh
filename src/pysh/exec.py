from typing import Any

from .command import Command
from .utils import *


def Exec(cmd: str | Command, *args: str, **kwargs: Any):
    if isinstance(cmd, str):
        cmd = Command(cmd)
    cmd.commit(*args, **kwargs)


def Exek(cmd):
    # TODO: exe and kapture. maybe use better name.
    pass
