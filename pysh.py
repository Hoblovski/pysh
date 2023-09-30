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
            case RedirKind.FILE, path:
                kwargs['stdout'] = ensure_path(path).open('w')
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
            case RedirKind.FILE, path:
                kwargs['stderr'] = ensure_path(path).open('w')
            case RedirKind.PIPE:
                assert False
            case RedirKind.CAPTURE:
                assert False
        match self.stdin:
            case RedirKind.NOREDIR:
                kwargs['stdin'] = None,
            case RedirKind.NULL:
                kwargs['stdin'] = subprocess.DEVNULL,
            case RedirKind.ERR2OUT:
                assert False
            case RedirKind.FILE, path:
                kwargs['stdin'] = ensure_path(path).open('r')
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
            # This leaves proc1 unclosed, leaking.
            # But it is fine.
            return proc2

    def __call__(self, *args, **kwargs):
        res = copy.deepcopy(self)
        res.update_attr(*args, **kwargs)
        return res

    def __or__(self, cmd):
        # Note: p1 | p2 return p2, henceforth losing any further updates to p1.
        if not isinstance(cmd, Command):
            raise Exception('Pipelining only happen on process. Likely you missed a parenthesis.')
        cmd.pipefrom = self
        return cmd

    def __str__(self):
        return ' '.join(self.args)

    def Exec(self, execarg=None):
        """Use == for command invocation.

        Rationale:
            Because __eq__ has the lowest precedence among custom-defineable operators.
            Fuck! Python's got chained comparison...
        """
        kwargs = self.subprocess_kwargs()
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

    def __gt__(self, target):
        # target: None for /dev/null, or str for file name
        if target is None:
            self.stdout = RedirKind.NULL
        else:
            self.stdout = RedirKind.FILE, target
        return self

    def __lt__(self, source):
        # target: None for /dev/null, or str for file name
        if source is None:
            self.stdin = RedirKind.NULL
        else:
            self.stdin = RedirKind.FILE, source
        return self

def Exec(cmd):
    cmd.Exec()
def Exek(cmd):
    # exe and kapture. maybe use better name.
    pass
echo = Command("echo")
sed = Command("sed")
cat = Command("cat")
x=echo("hello world")
y=sed('s/o/O/g')
z=sed("s/hellO/bye/g")
#echo("hello world") > 'o.log'                                           ==()
#echo("hello world") | sed('s/o/O/g')                                    ==()













print("Writing to o.txt")
Exec(   echo("hello world") | sed('s/o/O/g') | sed("s/^\S*/bye/") > "log"     )
print("Reading from o.txt")
Exec(   cat < "o.txt"    )

