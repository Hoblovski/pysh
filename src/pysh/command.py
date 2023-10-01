import shutil
import subprocess
import copy
import time
from enum import Enum, auto
from typing import Self, TypeAlias, Any
from pathlib import Path

from .utils import *


class PyShError(Exception):
    pass


class CommitResKind(Enum):
    """
    Value           Definition
    ================================
    SUCCESS         When the command returned zero.
    FAILED          When the command returned non-zero value.
    CRITICAL        When a Python exception is raised.
    TIMEOUT         When the command timed out.
    """

    SUCCESS = auto()
    FAILED = auto()
    CRITICAL = auto()
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


class PyShCommitError(PyShError):
    def __init__(self, res: CommitResult) -> None:
        self.res = res


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
            * You can use stdin for i, stdout for o, stderr for e.
              They are the same.

            Constraints:
            * o and a must not be present at the same time
            * i and stdin are exclusive. Same for o and stdout, e and stderr.

        PIPELINING
            The operator `|` is supported for pipelining.

            kwargs          meaning
            ===================
            pipefrom=cmd    self takes input from output of cmd i.e. cmd|self

        COMMAND SUBSTITUTION
            Capture command outputs like $( ... )

            kwargs          meaning
            ===================
            capture=1       capture stdout.
                            Use in combination with eo=1 to capture stderr.
    """

    def __init__(self, *args: str, **kwargs: Any) -> None:
        self.args: list[str] = []
        self.kwargs: dict[str, Any] = {}
        self.update(*args, **kwargs)

    def update(self, *args: str, **kwargs: Any) -> None:
        """Augment the command.
        Added parameters and options should be passed as `*args`.
        Information related to invocation of the command (redirection etc) is passed in `**kwargs`, such as redirections.

        Modifies self in-place.
        """
        args, kwargs = Command._normalized_args(args, kwargs)
        self.args += args
        self.kwargs.update(kwargs)

    def update_copy(self, *args: str, **kwargs: Any) -> Self:
        """Copy the command and augment it.
        Operates on a copy of self, leaving self intact.

        For details check update().
        """
        new = copy.deepcopy(self)
        new.update(*args, **kwargs)
        return new

    @staticmethod
    def _normalized_args(args, kwargs) -> tuple[Any, Any]:
        # stdout, stderr, stdin are aliases to o, e, i
        if (i := kwargs.pop("stdin", None)) is not None:
            kwargs["i"] = i
        if (o := kwargs.pop("stdout", None)) is not None:
            kwargs["o"] = o
        if (e := kwargs.pop("stderr", None)) is not None:
            kwargs["e"] = e
        # TODO: special handle "2>&1" ">xx" in args.
        return args, kwargs

    @staticmethod
    def _redir2str(redir: Any) -> str:
        match redir:
            case None | 0:
                return "/dev/null"
            case subprocess.PIPE:
                return "<pipe>"
            case str(s):
                return s
            case p if isinstance(p, Path):
                return str(p)
            case inv:
                raise ValueError(f"Invalid redirection {redir}")
        return ""  # XXX: why does mypy complain?

    def popen_inplace(self, *args: str, **kwargs: Any) -> subprocess.Popen:
        """Get the popen object used for this command.
        IMMEDIATELY spawns the process and starts execution.

        Modifies self in-place."""
        self.update(*args, **kwargs)
        if "pipefrom" not in self.kwargs:
            # self is not pipelined (or is the very first of a pipeline)
            kwargs = self._popen_kwargs()
            proc = subprocess.Popen(self.args, **kwargs)
            return proc
        else:
            proc1 = self.kwargs["pipefrom"].popen(o=subprocess.PIPE)
            kwargs = self._popen_kwargs(pipefrom=proc1.stdout)
            proc2 = subprocess.Popen(self.args, **kwargs)
            proc1.stdout.close()  # required
            return proc2

    def popen(self, *args: str, **kwargs: Any) -> subprocess.Popen:
        """Get the popen object used for this command.
        For details check popen_inplace().

        Operates on a copy of self."""
        new = copy.deepcopy(self)
        return new.popen_inplace(*args, **kwargs)

    def commit(self, *args: str, **kwargs) -> CommitResult:
        """Commit the command to system and execute it.

        kwargs: See Run()
        * input, timeout, strict, suppress
        """
        RUN_KEYS = ["timeout", "input", "strict"]
        run_kwargs = project_dict(kwargs, RUN_KEYS)
        kwargs = dict(kv for kv in kwargs.items() if kv[0] not in RUN_KEYS)
        time_start = time.perf_counter()
        with self.popen(*args, **kwargs) as proc:
            try:
                timeout = run_kwargs.get("timeout", None)
                input = run_kwargs.get("input", None)
                output, stderr = proc.communicate(input=input, timeout=timeout)
                # TODO: binary output
                stdout = output.decode() if output is not None else ""
                stderr = stderr.decode() if stderr is not None else ""
                elapsed = time.perf_counter() - time_start
                retcode = proc.poll()
                if retcode == 0:
                    kind = CommitResKind.SUCCESS
                else:
                    kind = CommitResKind.FAILED
                res = CommitResult(
                    kind, retcode, stdout=stdout, stderr=stderr, elapsed=elapsed
                )
                if retcode != 0 and run_kwargs.get("strict", False):
                    raise PyShCommitError(res)
                else:
                    return res
            except subprocess.TimeoutExpired as exc:
                elapsed = time.perf_counter() - time_start
                kind = CommitResKind.TIMEOUT
                retcode = proc.poll()
                proc.kill()
                proc.wait()
                stdout = exc.output.decode() if exc.output is not None else ""
                stderr = exc.stderr.decode() if exc.stderr is not None else ""
                res = CommitResult(
                    kind, retcode, stdout=stdout, stderr=stderr, elapsed=elapsed
                )
                if run_kwargs.get("strict", False):
                    raise PyShCommitError(res)
                else:
                    return res
            except Exception as exc:
                proc.kill()
                raise

    def __call__(self, *args: str, **kwargs):
        """Add new arguments and update options.
        Returns a new command without modifying self."""
        return self.update_copy(*args, **kwargs)

    def __or__(self, cmd: Self) -> Self:
        """Bash-like command pipelining.
        Creates a new command."""
        if not isinstance(cmd, Command):
            raise TypeError(f"Expected a Command object for pipelining. Got {cmd}")
        assert "pipefrom" not in cmd.kwargs
        return cmd.update_copy(pipefrom=copy.deepcopy(self))

    def __str__(self):
        res = []
        if (pipefrom := self.kwargs.get("pipefrom", None)) is not None:
            res += [str(pipefrom), "|"]
        for arg in self.args:
            if " " in arg:
                res += ['"' + arg + '"']
            else:
                res += [arg]
        if (i := self.kwargs.get("i", None)) is not None:
            res += ["<", Command._redir2str(i)]
        if (o := self.kwargs.get("o", None)) is not None:
            res += [">", Command._redir2str(o)]
        if (e := self.kwargs.get("e", None)) is not None:
            res += ["2>", Command._redir2str(e)]
        if (oe := self.kwargs.get("oe", None)) is not None:
            res += ["2>&1"]
        if (capture := self.kwargs.get("capture", None)) is not None:
            res = ["$("] + res + [")"]
        return " ".join(res)

    def _popen_kwargs(self, **kwargs) -> dict[str, Any]:
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
        if kwargs.get("capture", None) == 1:
            res["stdout"] = subprocess.PIPE
        # HANDLE: pipefrom
        if "pipefrom" in kwargs:
            res["stdin"] = kwargs["pipefrom"]
        # todo for pipes: kwargs["stdin"] = proc1.stdout
        return res
