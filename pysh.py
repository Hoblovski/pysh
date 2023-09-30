import pathlib
import shutil
import subprocess
import copy
from enum import Enum, auto
from typing import Sequence, Union

def ensure_path(p: Union[str, pathlib.Path]) -> pathlib.Path:
    if isinstance(p, pathlib.Path):
        return p
    if isinstance(p, str):
        return pathlib.Path(p)


class RedirKind(Enum):
    """Redirection kind for a specific descriptor.
    A redirection is characterized by its kind and associated data, represented
    as a tuple."""
    NOREDIR = auto()    #
    NULL = auto()       # >/dev/null ...
    ERR2OUT = auto()    # 2>&1, ONLY FOR OUR.
    FILE = auto()       # >f ...
    PIPE = auto()       # f1 | f2. stored, linked to next command
    CAPTURE = auto()    # $(f). stored.

class Command:
    def __init__(self, *args, **kwargs):
        self.init_attr()
        self.update_attr(*args, **kwargs)

    def init_attr(self):
        self.args = []
        self.stdin = RedirKind.NOREDIR,
        self.stdout = RedirKind.NOREDIR,
        self.stderr = RedirKind.NOREDIR,
        self.pipefrom = None

    @staticmethod
    def normalized_args(args, kwargs):
        # TODO: special handle "2>&1" ">xx" in args.
        # TODO: should we allow non-str in args, so we can echo(2)
        return args, kwargs

    def update_attr(self, *args, **kwargs):
        """
        type    **kwargs    meaning
        ===========================
        REDI-   (absence)  no redirect
        RECT    i=          <
                o=          >
                o=None,     >/dev/null
                o=0,        >/dev/null
                e=          2>
                a=          >>
                oe=         2>&1 >
                oe=1        2>&1
                oe=0        2>&1 >/dev/null
                oe=None     2>&1 >/dev/null
        """
        args, kwargs = Command.normalized_args(args, kwargs)
        self.args += args
        if 'i' in kwargs:
            assert False # TODO
        if 'o' in kwargs:
            assert False # TODO
        if 'e' in kwargs:
            assert False # TODO
        if 'a' in kwargs:
            assert False
        if 'oe' in kwargs:
            assert False

    def subprocess_kwargs(self):
        kwargs = {}
        match self.stdout:
            case RedirKind.NOREDIR:
                kwargs['stdout'] = None,
            case RedirKind.NULL:
                kwargs['stdout'] = subprocess.DEVNULL,
            case RedirKind.ERR2OUT:
                assert False
            case RedirKind.FILE:
                kwargs['stdout'] = ensure_path(self.stdout).open('w')
            case RedirKind.PIPE:
                assert False
            case RedirKind.CAPTURE:
                assert False
        match self.stderr:
            case RedirKind.NOREDIR:
                kwargs['stderr'] = None,
            case RedirKind.NULL:
                kwargs['stderr'] = subprocess.DEVNULL,
            case RedirKind.ERR2OUT:
                kwargs['stderr'] = subprocess.STDOUT,
            case RedirKind.FILE:
                kwargs['stderr'] = ensure_path(self.stderr).open('w')
            case RedirKind.PIPE:
                assert False
            case RedirKind.CAPTURE:
                assert False
        return kwargs

    def popen(self, **kwargs):
        if self.pipefrom is None:
            return subprocess.Popen(self.args, **kwargs)
        else:
            proc1 = self.pipefrom.popen(stdout=subprocess.PIPE)
            kwargs['stdin'] = proc1.stdout
            proc2 = subprocess.Popen(self.args, **kwargs)
            proc1.stdout.close()
            return proc2 # when close proc1?

    def __call__(self, *args, **kwargs):
        res = copy.deepcopy(self)
        res.update_attr(*args, **kwargs)
        return res

    def __or__(self, cmd):
        if not isinstance(cmd, Command):
            raise Exception('Pipelining only happen on process. Likely you missed a parenthesis.')
        return cmd.set_pipefrom(self)

    def set_pipefrom(self, cmd):
        # from|self
        self.pipefrom = cmd
        return self

    def __matmul__(self, execarg):
        if execarg != ():
            return NotImplemented
        kwargs = self.subprocess_kwargs()
        print('hh;')
        with self.popen(**kwargs) as proc:
            try:
                stdout, stderr = proc.communicate()
            except TimeoutExpired as exc:
                proc.kill()
                proc.wait()
                raise
            except:
                proc.kill()
                raise
            retcode = proc.poll()
            if retcode:
                raise subprocess.CalledProcessError(retcode, proc.args,
                        output=stdout, stderr=stderr)



C = Command
echo = C("echo")
sed = C("sed")
x=echo("hello world")
x@()
y=sed('s/o/O/g')
(x|y)@()
z=C("sed", "s/hellO/bye/g")
(x|y|z)@()
