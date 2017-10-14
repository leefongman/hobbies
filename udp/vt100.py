#!/usr/bin/env python3

"""
常量定义
"""
#  VT码标识
VT = "\033["
#  光标操作定义
SAVE, LOAD = VT + "s", VT + "u"

#  清除操作定义
SCREEN, LINE = VT + "2J", VT + "2K"


def goto(x, y):
    """
    定位到屏幕x行y列
    """
    return VT + "%d;%dH" % (x, y)

