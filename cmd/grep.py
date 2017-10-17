#!/usr/bin/env python3

import sys
import os

def grepFile(key, filePath, op=0):
    f = open(filePath).readlines()
    dt = len(str(len(f)))
    fpath = ['', "\033[35m%s\033[34m:" % filePath][op]
    reKey = "\033[31m" + key + "\033[0m"

    for index, line in enumerate(f):
        if key in line:
            left = (fpath + "\033[32m%s\033[34m:\033[0m" %
                    (str(index + 1).rjust(dt)))
            content = line.replace(key, reKey)
            print(left + content, end='')


def grepDir(key, dirPath):
    sep = os.path.sep
    dirList = os.listdir(dirPath)
    dirList = [dirPath + sep + p for p in dirList]

    for path in dirList:
        if os.path.isdir(path):
            grepDir(key, path)
        else:
            try:
                grepFile(key, path, 1)
            except:
                pass


def grep(key, path, op=0):
    path = path[:-1] if path[-1] == os.path.sep else path
    if os.path.isdir(path):
        grepDir(key, path)
    elif os.path.isfile(path):
        grepFile(key, path, op)
    else:
        print("grep: %s: 没有那个文件或目录" % path)


def main(argv):
    length = len(argv)
    if length < 3:
        print("缺少参数")
    elif length == 3:
        grep(argv[1], argv[2])
    else:
        for idx in range(length - 2):
            grep(argv[1], argv[idx + 2], 1)


if __name__ == "__main__":
    main(sys.argv)
