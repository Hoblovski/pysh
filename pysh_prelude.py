from pysh import Command

# We have Pythonic alternatives
ls_ = "ls"
echo_ = "echo"
cat_ = "cat"
cp_ = "cp"
mkdir_ = "mkdir"
rm_ = "rm"
mv_ = "mv"
tee_ = "tee"


# Usually used commands. Defined here so users do not have to type
def predefine_command(*args):
    for arg in args:
        globals()[arg] = Command(arg)


# See your most used commands with the command:
#   $ history | awk '{print $2}' | sort | uniq -c | sort -hr | head -n 50
# Keep this list sorted!
predefine_command(
    "chmod" "echo",
    "fd",
    "find",
    "git",
    "git",
    "grep",
    "head",
    "make",
    "rg",
    "sed",
    "sort",
    "tail",
    "vim",
)
