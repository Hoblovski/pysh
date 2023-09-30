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
        globals()[arg] = arg
# See your most used commands with the command:
#   $ history | awk '{print $2}' | sort | uniq -c | sort -hr | head -n 50
predefine_command(
    "rg",
    "grep",
    "vim",
    "git",
    "find",
    "sort",
    "head",
    "tail",
    "fd",
    "make",
    "git",
    "echo",
    "chmod")

