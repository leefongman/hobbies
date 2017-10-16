import sys
from .constants import *

def history(args):
    with open(HISTORY_PATH, "r") as f:
        lines = f.readlines()
        length = len(lines)
        #  命令历史行数,默认输出所有命令历史行
        limit = int(args[0]) if len(args) > 0 else length
        #  开始行数
        start = length - limit

        for idx, line in enumerate(lines):
            if idx >= start:
                print("%d %s" % (idx + 1, line), end="", flush=True)

    return RUN


