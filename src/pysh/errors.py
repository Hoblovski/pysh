from . import command


class PyShError(Exception):
    pass


class PyShCommitError(PyShError):
    def __init__(self, res: "command.CommitResult") -> None:
        self.res = res
