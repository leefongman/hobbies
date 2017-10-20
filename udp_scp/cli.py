#!/usr/bin/env python3

import udp
import sys
import packet
import os
import getpass

def checkArgc(argc):
    """
    检查参数个数是否满足条件
    """
    if argc < 2:
        return print("请指定服务器和验证信息")
    elif argc > 3:
        return print("有多余的参数")

    return True


def getUser(data, mes):
    """
    提取用户名
    """
    if '@' not in mes or mes[0] == '@':
        data["user"], mes = os.getlogin(), mes.split('@', 1)[-1]
    else:
        data["user"], mes = mes.split('@', 1)

    return mes


def getPath(data, mes):
    """
    提取文件具体路径
    """
    if ':' not in mes or mes[0] == ':':
        return print("缺少服务器参数或文件路径参数")

    ip, *mes = mes.split(':')

    if not mes:
        return print("请指定文件路径")
    elif len(mes) == 1:
        port, data["path"] = 9000, mes[0]
    elif len(mes) == 2:
        port, data["path"] = mes

    if data["path"][0] != '/':
        return print("请指定绝对路径")

    data["path"] = os.path.realpath(data["path"])

    return ip, port


def getSavePath(data, argv):
    if len(argv) == 3:
        dstpath = os.path.realpath(argv[2])
        if os.path.isdir(dstpath):
            dstpath += '/' + os.path.basename(data["path"])
    else:
        dstpath = os.path.basename(data["path"])

    if os.path.exists(dstpath) and input("是否覆盖(Y/N): ") not in "Yy":
        return

    return dstpath


def parseArgs(argv):
    argc = len(argv)

    if not checkArgc(argc):
        return

    mes = argv[1]
    data = {}
    mes = getUser(data, mes)
    obj = getPath(data, mes)

    if not obj:
        return

    ip, port = obj
    dstpath = getSavePath(data, argv)

    if not dstpath:
        return

    data["pwd"] = getpass.getpass()
    if not data["pwd"]:
        return print("密码不能为空")

    return ip, int(port), dstpath, data


def exitStr(sd, s):
    sd.close()
    return print(s)


def recvWrite(f, sd):
    while True:
        data = packet.recv(sd, timeout=5.0)
        if not data:
            return exitStr(sd, "接收数据包失败")
        data, addr = data
        if data["type"] == packet.DATA:
            f.write(data["data"])

            if not packet.send(sd, None, addr, packet.DATA_ACK):
                return exitStr(sd, "发送数据回应包失败")

        elif data["type"] == packet.SHUTDOWN:
            break

    return True


def main():
    data = parseArgs(sys.argv)

    if not data:
        return

    ip, port, dstpath, data = data

    sd = udp.createCli((ip, port), data)
    if not sd:
        return print("连接服务器失败")

    data = packet.recv(sd, timeout=5.0)
    if not data:
        return exitStr(sd, "连接服务器失败")

    data, addr = data
    print(data)
    if data["type"] == packet.ERROR:
        return exitStr(sd, packet.ERRORMES[data["code"]])

    f = open(dstpath, "wb")
    if not recvWrite(f, sd):
        return

    f.flush()
    f.close()
    sd.close()


if __name__ == "__main__":
    main()

