from .constants import *

def cd(args):
    newDir = args[0] if len(args) > 0 else os.getenv("HOME")
    if "~" in newDir:
        newDir = newDir.replace("~", os.getenv("HOME"))

    os.chdir(newDir)

    return RUN
