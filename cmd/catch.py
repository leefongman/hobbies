#!/usr/bin/env python3

import sys
import os

def readPrint(arg, flag, start):
    """
    按行打印文件内容(加行号或不加行号)
    """
    if not os.path.exists(arg):
        print("cat: %s: 没有那个文件或目录" % arg)
        return

    if os.path.isdir(arg):
        print("cat: %s: 是一个目录" % arg)
        return

    for line in open(arg, "r"):
        s = "\033[36m%6d\033[0m " % start if flag else ""
        print(s + line, end="")
        start += 1

    return start

def main(argv):
    """
    主程序
    """
    if len(argv) < 2:
        print("缺少参数")
        return

    #  默认不加行号打印模式
    flag = False
    start = 1
    del argv[0]

    if "-n" in argv:
        flag = True
        argv.remove("-n")

    #  打印所有文件内容
    for arg in argv:
        start = readPrint(arg, flag, start)


if __name__ == "__main__":
    main(sys.argv)
