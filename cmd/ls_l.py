#!/usr/bin/env python3

import sys
import os
from stat import *


#  颜色声明
BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, WHITE, DEFAULT = range(30, 39)

#  文件类型->颜色映射字典声明
color = {
        "b": RED, "x": GREEN, "p": YELLOW, "d": BLUE,
        "s": PURPLE, "l": CYAN, "c": WHITE, "-": DEFAULT
        }

#  所属权限字典声明
perm = {
        "u": {"r": S_IRUSR, "w": S_IWUSR, "x": S_IXUSR, "s": S_ISUID},
        "g": {"r": S_IRGRP, "w": S_IWGRP, "x": S_IXGRP, "s": S_ISGID},
        "o": {"r": S_IROTH, "w": S_IWOTH, "x": S_IXOTH, "s": S_ISVTX}
        }


def getColor(s, colorNum):
    """
    返回带VT颜色编码的字符串
    """
    return "\033[1;%dm%s\033[0m" % (colorNum, s)


def getType(mode):
    """
    返回文件类型
    """
    return " pc d b - l s"[S_IFMT(mode) >> 12]


def getPerm(mode, op=None):
    """
    返回文件操作权限
    """
    if op:
        tail = ["-x"[perm[op]["x"] & mode != 0], ["ST"[op == "o"],
            "st"[op == "o"]][perm[op]["x"] & mode != 0]][perm[op]["s"]
                    & mode != 0]

        return "-r"[perm[op]["r"] & mode != 0] + "-w"[perm[op]["w"] &
                mode != 0] + tail

    return getPerm(mode, "u") + getPerm(mode, "g") + getPerm(mode, "o")



def getMode(mode):
    """
    返回文件完整权限
    """
    return getType(mode) + getPerm(mode)


def getOwn(idOwn, path):
    """
    通过所属用户(组)id获取所属用户(组)名
    """
    for line in open(path):
        ls = line.split(":")
        if str(idOwn) == ls[2]:
            return ls[0]


def isYear(y):
    """
    判断y年是否为闰年
    """
    return y % 4 == 0 and y % 100 !=0 or y % 400 == 0


def daysOfYear(y):
    """
    返回y年的天数
    """
    return 365 + isYear(y)


def days2Year(y1, y2):
    """
    返回y1到y2年之间的总天数
    """
    if y2 == y1:
        return 0

    return days2Year(y1, y2 - 1) + daysOfYear(y2 - 1)


def daysOfMonth(y, m):
    """
    返回y年m月的天数
    """
    ls = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if m == 2:
        return ls[1] + isYear(y)

    return ls[m - 1]


def daysMonths(y, m):
    """
    返回y年1到m月的总天数
    """
    if m == 1:
        return 0

    return daysMonths(y, m - 1) + daysOfMonth(y, m - 1)


def getDate(mtime):
    """
    通过时间戳获得日期时间
    """
    #  1分钟的秒数
    sOfm = 60
    #  1小时的秒数
    sOfh = sOfm * 60
    #  1天的秒数
    sOfD = sOfh * 24

    #  北京时间戳换算
    mtime = int(mtime) + 8 * sOfh
    #  累计天数
    days = mtime // sOfD

    #  计算年
    Y = days // 365 + 1970 + 1
    while days2Year(1970, Y)  > days:
        Y -= 1

    #  剩余天数
    days -= days2Year(1970, Y)

    #  计算月
    M = days // 30 + 1
    while daysMonths(Y, M)  > days:
        M -= 1

    #  计算日
    D = days - daysMonths(Y, M) + 1

    #  计算时
    h = int(mtime % sOfD / sOfh)

    #  计算分
    m = int(mtime % sOfh / sOfm)

    return "%d/%02d/%02d %02d:%02d" % (Y, M, D, h, m)


def getNameLs(arg):
    """
    返回文件名列表和文件路径列表
    """
    #  目标路径为文件
    if os.path.isfile(arg):
        return [arg.split("/")[-1]], [arg]

    #  目标路径为目录
    elif os.path.isdir(arg):
        lP = os.listdir(arg)
        lP.sort()
        listP = [arg + ["/", ""][arg[-1] == "/"] + path for path in lP]
        return lP, listP

    #  目标路径不存在
    else:
        print("目标路径'%s'不存在" % arg)


def colorName(mode, path, name):
    if mode[0] == "-" and "x" in mode:
        return getColor(name, color["x"])

    name = getColor(name, color[mode[0]])

    if mode[0] == "l":
        return name + " -> " + getColor(os.readlink(path), GREEN)

    return name


def getLs(arg):
    """
    获取文件属性列表,方便输出对齐
    """
    lP, listP = getNameLs(arg)

    ls = [[] for i in range(6)]
    for path in listP:
        ls[0].append(getMode(os.lstat(path).st_mode))
        ls[1].append(str(os.lstat(path).st_nlink))
        ls[2].append(getOwn(os.lstat(path).st_uid, "/etc/passwd"))
        ls[3].append(getOwn(os.lstat(path).st_gid, "/etc/group"))
        ls[4].append(str(os.lstat(path).st_size))
        ls[5].append(getDate(os.lstat(path).st_mtime))

    ls.append([colorName(mode, path, name) for name, path, mode
        in zip(lP, listP, ls[0])])

    return ls


def getDt(ls):
    """
    获取列表中元素字符串形式的最大长度
    """
    ls = [len(str(value)) for value in ls]

    return max(ls)


def main(argv):
    ls = getLs(argv[1])
    for i in range(len(ls[0])):
        if ls[6][i][0] != ".":
            print(ls[0][i], ls[1][i].rjust(getDt(ls[1])),
                    ls[2][i].rjust(getDt(ls[2])),
                    ls[3][i].rjust(getDt(ls[3])),
                    ls[4][i].rjust(getDt(ls[4])),
                    ls[5][i], ls[6][i])

if __name__ == "__main__":
    main(sys.argv)
