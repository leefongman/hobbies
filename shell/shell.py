#!/usr/bin/env python3

import os
import sys
import getpass
import socket
import signal
from subprocess import call, Popen, PIPE
from command import *
from prompt_toolkit import prompt
from prompt_toolkit.history import  FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter


#  用于命令补全
shellCompleter = WordCompleter(["cd", "ls", "pwd", "ps"], ignore_case=True)
#  用于存储命令与处理函数的映射关系
cmdDict = {}

class Task:
    """
    命令任务类
    """
    def __init__(self):
        self.args = []
        self.type = "NORMAL"


def prepro(cmd):
    """
    命令预处理
    """
    new = []
    #  初始化命令类型和命令列表
    cmdType, args = "NORMAL", []

    #  解决环境变量获取问题
    for token in cmd:
        newToken = os.getenv(token[1:]) if token[0] == "$" else token
        new.append(newToken)

    for idx, token in enumerate(new):
        #  管道
        if token == "|":
            cmdType = "PIPE"
            args.append(new[0: idx])
            args.append(new[idx + 1:])
            break
        #  重定向
        elif token in ["<", ">", "2>", "&>"]:
            cmdType = "RE"
            break

    if cmdType != "PIPE":
        args = new

    return cmdType, args


def init(cmd):
    fout = sys.stdout
    fin = sys.stdin
    ferr = sys.stderr
    cmdType, args = prepro(cmd)

    return fout, fin, ferr, cmdType, args


def runNormal(args, fout, fin, ferr):
    if args[0] in cmdDict:
        return cmdDict[args[0]](args[1:])
    else:
        call(args, stdout=fout, stdin=fin, stderr=ferr)


def re(args, ch, mode):
    """
    重定向操作预处理
    """
    f = open(args[args.index(ch) + 1], mode)
    args.remove(args[args.index(ch) + 1])
    args.remove(ch)

    return f


def runRe(args, fout, fin, ferr):
    """
    执行重定向命令
    """
    if ">" in args:
        fout = re(args, ">", "w")
    elif "<" in args:
        fin = re(args, "<", "r")
    elif "2>" in args:
        ferr = re(args, "2>", "w")
    elif "&>" in args:
        ferr = re(args, "&>", "w")
    call(args, stdout=fout, stdin=fin, stderr=ferr)


def runPipe(args):
    """
    执行管道命令
    """
    pro = Popen(args[0], bufsize=1024, stdin=PIPE, stdout=PIPE,
            close_fds=True)
    fout = pro.stdout
    call(args[1], stdin=fout)


def run(cmd):
    """
    命令实现过程
    """
    fout, fin, ferr, cmdType, args = init(cmd)
    if cmdType == "NORMAL":
        runNormal(args, fout, fin, ferr)
    elif cmdType == "RE":
        runRe(args, fout, fin, ferr)
    elif cmdType == "PIPE":
        runPipe(args)

    return RUN


def showConsole():
    """
    返回用于控制台显示的字符串
    """
    #  获取当前用户名和主机名
    user, hostname = getpass.getuser(), socket.gethostname()

    #  获取当前工作目录
    cwd = os.getcwd()

    #  使用"~"替代用户家目录
    homeDir = os.getenv("HOME")
    if cwd >= homeDir:
        cwd = cwd.replace(homeDir, "~")

    return "%s@%s %s\n$" % (user, hostname, cwd)


def ignoreSig():
    """
    忽略Ctrl + z和Ctrl + c退出信号
    """
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def shlLoop():
    """
    shell程序循环主体
    """
    call(["clear"])
    status = RUN
    ignoreSig()

    while status:
        ppt = showConsole()

        try:
            cmd = prompt(ppt, history=FileHistory(HISTORY_PATH),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=shellCompleter).split()
            status = run(cmd)
        except:
            _, error, _ = sys.exc_info()
            print(error)


def regCmd(name, func):
    """
    注册命令,建立命令与处理函数之间的映射关系
    name: 命令名
    func: 函数名
    """
    cmdDict[name] = func


def regAllCmd():
    """
    注册所有命令
    """
    regCmd("cd", cd)
    regCmd("exit", exit)
    regCmd("export", export)
    regCmd("getenv", getenv)
    regCmd("history", history)
    regCmd("grep", grep)
    regCmd("cat", cat)


def main():
    """
    主程序
    """
    regAllCmd()
    shlLoop()

if __name__ == "__main__":
    main()
