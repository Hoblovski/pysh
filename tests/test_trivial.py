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


# def test_strict():
#    res = Run("flse"
#
#
#
# def test_if():
#    #if grep
