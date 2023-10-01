import pytest

from pysh import *

echo = Command("echo")
cat = Command("cat")


def test_triv():
    assert Cap(echo, "hello world") == "hello world"


def test_twice():
    cmd = echo("hello")
    Run(cmd)
    Run(cmd)


def test_pipe_twice():
    x = echo("hello world")
    y = sed("s/o/O/g")
    z = sed("s/hellO/bye/g")
    res = Cap(x | y | z)
    assert res == "bye wOrld"
    res = Cap(x | y | z, strip=False)
    assert res == "bye wOrld\n"
    res = Cap(x | y | z)
    assert res == "bye wOrld"


def test_redirect(tmp_path):
    Run(echo("lorem ipsum"), stdout=tmp_path / "o0.log")
    assert (tmp_path / "o0.log").read_text() == "lorem ipsum\n"
    Run(echo("hello world") | sed("s/^\\S*/bye/"), o=tmp_path / "o.log")
    res = Cap(cat, tmp_path / "o.log")
    assert res == "bye world"


def test_strict():
    with pytest.raises(PyShCommitError):
        Run("false", strict=True)
    with pytest.raises(PyShCommitError):
        Cap("false", strict=True)
    with pytest.raises(PyShCommitError):
        Cap("yes", timeout=0.1, strict=True)


def test_bool():
    assert Run("true")
    assert not Run("false")
    assert Run("ls", o=None)


def test_suppress():
    with pytest.raises(FileNotFoundError):
        Run("CrAzY-NoNeXiStEnT-CoMmAnD")
    res = Run("CrAzY-NoNeXiStEnT-CoMmAnD", suppress=True)
    assert res.kind == CommitResKind.CRITICAL
