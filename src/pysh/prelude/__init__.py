from ..command import Command


def predefine_command(*args):
    """Define commands. Makes code clearer and saves quote keystrokes"""
    for arg in args:
        globals()[arg] = Command(arg)


def predefine_command_alt(*args):
    """Define commands which a pysh-builtin alternative exists."""
    for arg in args:
        globals()[arg + "_"] = Command(arg)


# See your most used commands with the command:
#   $ history | awk '{print $2}' | sort | uniq -c | sort -hr | head -n 50
# Keep this list sorted!
predefine_command(
    "chmod",
    "fd",
    "tr",
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
    "touch",
)


predefine_command_alt(
    "ls",
    "echo",
    "cat",
    "cp",
    "mkdir",
    "rm",
    "mv",
    "tee",
)
