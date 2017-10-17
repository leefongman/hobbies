from .constants import *

def grep(args):
    f = open(args[1], "r").readlines()
    dt = len(str(len(f)))
    key = args[0]
    reKey = "\033[36m" + key + "\033[0m"

    for index, line in enumerate(f):
        if key in line:
            left = "\033[33m%s\033[32m:\033[0m" % (str(index + 1).rjust(dt))
            content = line.replace(key, reKey)
            print(left + content, end="")

    return RUN
