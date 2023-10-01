import shutil
import subprocess
import copy
import time
from enum import Enum, auto
from typing import Self, TypeAlias, Any
from pathlib import Path

from .utils import *


class CommitResKind(Enum):
    SUCCESS = auto()
    FAILED = auto()
    TIMEOUT = auto()


# TODO: should be a dataclass
class CommitResult:
    def __init__(
        self,
        kind: CommitResKind,
        retcode: None | int,
        stdout: bytes | str = "",
        stderr: bytes | str = "",
        elapsed: float | None = None,
    ) -> None:
        self.kind = kind
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr
        self.elapsed = elapsed

    def __bool__(self) -> bool:
        return self.kind == CommitResKind.SUCCESS


class Command:
    """A command represents a bash command.
    It can be created, edited (adding parameter or set redirection), pipelined.
    It is NOT executed unless explicitly `commit`ed.

    NOTE while in principle we can override comparison operators for output redirection,
    Python's chained comparisons lead to weird behaviour.
    Python parses `f >o.txt <i.txt` as `f > o.txt and o.txt < i.txt`.

    Keyword arguments for self.kwargs:
        REDIRECTION
            Missing entries indicate that no redirection should happen.

            kwargs      meaning
            ===================
            i=path      <
            o=path      >
            e=path      >
            a=path      >>
            eo=1        2>&1
            #TODO: ii=  <<<

            Special paths:
            * 0 and None    : indicate /dev/null

            Constraints:
            * o and a must not be present at the same time

        PIPELINING
            The operator `|` is supported for pipelining.

            kwargs          meaning
            ===================
            pipefrom=cmd    self takes input from output of cmd i.e. cmd|self
    """

    def __init__(self, *args: str, **kwargs: Any) -> None:
        self.args: list[str] = []
        self.kwargs: dict[str, Any] = {}
        self.update(*args, **kwargs)

    def update(self, *args: str, **kwargs: Any) -> None:
        """Augment the command.
        Added parameters and options should be passed as `*args`.
        Information related to invocation of the command (redirection etc) is passed in `**kwargs`, such as redirections.
        """
        args, kwargs = Command.normalized_args(args, kwargs)
        self.args += args
        self.kwargs.update(kwargs)

    @staticmethod
    def normalized_args(args, kwargs) -> tuple[Any, Any]:
        # TODO: special handle "2>&1" ">xx" in args.
        return args, kwargs

    def popen(self, *args: str, **kwargs) -> subprocess.Popen:
        """Get the popen object used for this command.
        IMMEDIATELY spawns the process and starts execution.
        """
        self.update(*args, **kwargs)
        if "pipefrom" not in self.kwargs:
            # self is not pipelined (or is the very first of a pipeline)
            kwargs = self.popen_kwargs()
            proc = subprocess.Popen(self.args, **kwargs)
            return proc
        else:
            proc1 = self.kwargs["pipefrom"].popen(o=subprocess.PIPE)
            kwargs = self.popen_kwargs(pipefrom=proc1.stdout)
            proc2 = subprocess.Popen(self.args, **kwargs)
            proc1.stdout.close()  # required
            return proc2

    def commit(self, *args: str, **kwargs):
        """Commit the command to system and execute it.

        kwargs:
        * input: override as stdin data
        * timeout: timeout. Default in seconds, but accepts [smh] suffices too.
        """
        RUN_KEYS = ["timeout", "input"]
        run_kwargs = dict(kv for kv in kwargs.items() if kv[0] in RUN_KEYS)
        kwargs = dict(kv for kv in kwargs.items() if kv[0] not in RUN_KEYS)
        time_start = time.perf_counter()
        with self.popen(*args, **kwargs) as proc:
            try:
                timeout = run_kwargs.get("timeout", None)
                input = run_kwargs.get("input", None)
                stdout, stderr = proc.communicate(input=input, timeout=timeout)
                elapsed = time.perf_counter() - time_start
                retcode = proc.poll()
                if retcode == 0:
                    kind = CommitResKind.SUCCESS
                else:
                    kind = CommitResKind.FAILED
                return CommitResult(
                    kind, retcode, stdout=stdout, stderr=stderr, elapsed=elapsed
                )
            except subprocess.TimeoutExpired as exc:
                elapsed = time.perf_counter() - time_start
                kind = CommitResKind.TIMEOUT
                retcode = proc.poll()
                proc.kill()
                proc.wait()
                stdout = exc.output.decode() if exc.output is not None else ""
                stderr = exc.stderr.decode() if exc.stderr is not None else ""
                return CommitResult(
                    kind, retcode, stdout=stdout, stderr=stderr, elapsed=elapsed
                )
            except Exception as exc:
                proc.kill()
                raise

    def __call__(self, *args: str, **kwargs):
        """Add new arguments and update options. Returns a new command without modifying self."""
        new = copy.deepcopy(self)
        new.update(*args, **kwargs)
        return new

    def __or__(self, cmd: Self) -> Self:
        """Bash-like command pipelining."""
        if not isinstance(cmd, Command):
            raise TypeError(f"Expected a Command object for pipelining. Got {cmd}")
        assert "pipefrom" not in cmd.kwargs
        cmd.kwargs["pipefrom"] = self
        return cmd

    def __str__(self):
        raise NotImplementedError("TODO")

    def popen_kwargs(self, **kwargs) -> dict[str, Any]:
        """Interfacing python commands with system commands."""
        res: dict[str, Any] = {}
        kwargs = self.kwargs | kwargs
        # HANDLE: a o e i
        for kwname, resname, openflags in [
            ("a", "stdout", "a"),
            ("o", "stdout", "w"),
            ("e", "stderr", "w"),
            ("i", "stdin", "r"),
        ]:
            if kwname not in kwargs:
                continue
            match kwargs[kwname]:
                case None | 0:
                    res[resname] = None
                case subprocess.PIPE:
                    res[resname] = subprocess.PIPE
                case str(s):
                    res[resname] = open(s, openflags)  # TODO: close
                case p if isinstance(p, Path):
                    res[resname] = p.open(openflags)
                case inv:
                    raise ValueError(f'Invalid kwargs["{kwname}"]: {inv}')
        # HANDLE: eo
        if kwargs.get("eo", None) == 1:
            res["stderr"] = subprocess.STDOUT
        # HANDLE: pipefrom
        if "pipefrom" in kwargs:
            res["stdin"] = kwargs["pipefrom"]
        # todo for pipes: kwargs["stdin"] = proc1.stdout
        return res
