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


def test_redirect_capture(tmp_path):
    # Capture and redirect works fine
    assert Cap(echo("hello world"), o=None) == ""
    assert Cap(echo("hello world"), o=tmp_path / "t.txt") == ""
    # Does not capture stderr
    assert Cap(ls_("/NonEXISTENT")) == ""


def test_redirect_pipe(tmp_path):
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


def test_redir_null(capfd):
    cmd = ls_("/NonEXISTENT", ".")
    res = Run(cmd)
    stdout, stderr = capfd.readouterr()
    assert stdout != "" and stderr != ""
    res = Run(cmd, o=0)
    stdout, stderr = capfd.readouterr()
    assert stdout == "" and stderr != ""
    res = Run(cmd, e=0)
    stdout, stderr = capfd.readouterr()
    assert stdout != "" and stderr == ""
    res = Run(cmd, eo=0)
    stdout, stderr = capfd.readouterr()
    assert stdout == "" and stderr == ""
    res = Run(cmd, eo=1)
    stdout, stderr = capfd.readouterr()
    assert stdout != "" and stderr == ""


def test_capture_kwargs():
    cmd = ls_("/NonEXISTENT", ".")
    res = Run(cmd, capture=True)
    stdout, stderr = res.stdout, res.stderr
    assert stdout != "" and stderr != ""
    res = Run(cmd, o=0, capture=True)
    stdout, stderr = res.stdout, res.stderr
    assert stdout == "" and stderr != ""
    res = Run(cmd, e=0, capture=True)
    stdout, stderr = res.stdout, res.stderr
    assert stdout != "" and stderr == ""
    res = Run(cmd, eo=0, capture=True)
    stdout, stderr = res.stdout, res.stderr
    assert stdout == "" and stderr == ""
    res = Run(cmd, eo=1, capture=True)
    stdout, stderr = res.stdout, res.stderr
    assert stdout != "" and stderr == ""


def test_cap(capfd):
    # cap only captures stdout, while capture kwargs also captures stderr
    cmd = ls_("/NonEXISTENT", ".")
    res = Cap(cmd)
    assert res != ""
    stdout1, stderr1 = capfd.readouterr()
    assert stdout1 == "" and stderr1 != ""
    res = Cap(cmd, o=0)
    assert res == ""
    stdout1, stderr1 = capfd.readouterr()
    assert stdout1 == "" and stderr1 != ""
    res = Cap(cmd, e=0)
    assert res != ""
    stdout1, stderr1 = capfd.readouterr()
    assert stdout1 == "" and stderr1 == ""
    res = Cap(cmd, eo=0)
    assert res == ""
    stdout1, stderr1 = capfd.readouterr()
    assert stdout1 == "" and stderr1 == ""
    res = Cap(cmd, eo=1)
    assert res != ""
    stdout1, stderr1 = capfd.readouterr()
    assert stdout1 == "" and stderr1 == ""


def test_suppress():
    with pytest.raises(FileNotFoundError):
        Run("CrAzY-NoNeXiStEnT-CoMmAnD")
    res = Run("CrAzY-NoNeXiStEnT-CoMmAnD", suppress=True)
    assert res.kind == CommitResKind.CRITICAL


def test_cd(tmp_path):
    with ChDir(tmp_path):
        Run(touch, "a")
        Run(touch, "b")
        assert sorted(Cap(ls_).splitlines()) == ["a", "b"]
        Run(mkdir_, "c")
        with ChDir("c"):
            Run(touch, "d", "e")
            assert sorted(Cap(ls_).splitlines()) == ["d", "e"]
        assert sorted(Cap(find, ".").splitlines()) == [
            ".",
            "./a",
            "./b",
            "./c",
            "./c/d",
            "./c/e",
        ]
