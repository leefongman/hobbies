from .constants import *

def readPrint(args, flag, start):
    """
    按行打印文件内容(加行号或不加行号)
    """
    for line in open(args, "r"):
        s = "\033[36m%6d\033[33m  " % start if flag else ""
        print(s + line + "\033[0m", end="")
        start += 1

def cat(args):
    """
    主程序
    """
    #  没有传参时提示缺少参数
    if len(args) < 1:
        print("缺少参数")
        return

    #  默认不加行号打印模式
    flag = False
    start = 1

    #  参数中有"-n"时,去除参数"-n",并转为加行号打印模式
    if "-n" in args:
        flag = True
        args.remove("-n")


    #  打印所有文件内容
    for arg in args:
        readPrint(arg, flag, start)
        start += len(arg)

    return RUN
