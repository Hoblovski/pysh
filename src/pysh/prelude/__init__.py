"""The list of predefined commands is flexible. You can see your most frequently used commands with
$ history | awk '{print $2}' | sort | uniq -c | sort -hr | head -n 50"""
from ..command import Command

chmod = Command("chmod")
fd = Command("fd")
tr = Command("tr")
find = Command("find")
git = Command("git")
git = Command("git")
grep = Command("grep")
head = Command("head")
make = Command("make")
rg = Command("rg")
sed = Command("sed")
sort = Command("sort")
tail = Command("tail")
vim = Command("vim")
touch = Command("touch")

ls_ = Command("ls")
echo_ = Command("echo")
cat_ = Command("cat")
cp_ = Command("cp")
mkdir_ = Command("mkdir")
rm_ = Command("rm")
mv_ = Command("mv")
tee_ = Command("tee")
