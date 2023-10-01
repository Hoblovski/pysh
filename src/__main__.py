from .pysh import *

echo = Command("echo")
cat = Command("cat")

x = echo("hello world")
y = sed("s/o/O/g")
z = sed("s/hellO/bye/g")
Exec(x | y | z)

print("Writing to o.log")
Exec(echo("hello world") | sed("s/o/O/g") | sed("s/^\S*/bye/"), o="o.log")
print("Reading from o.log")
Exec(cat, "o.log")
