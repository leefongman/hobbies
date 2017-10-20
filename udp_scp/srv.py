#!/usr/bin/env python3

import udp
import sys
import os
import packet
import spwd
import crypt

#  每次读文件的最大长度
MAXSIZE = 512


def sendErr(sd, code, addr):
    return packet.send(sd, {"code": code}, addr, packet.ERROR)


def checkConnData(data):
    if not data or not ("user" in data and "pwd" in data and "path" in data):
        return 3

    try:
        sp = spwd.getspnam(data["user"])
    except:
        return 0

    if crypt.crypt(data["pwd"], sp.sp_pwdp) != sp.sp_pwdp:
        return 1

    try:
        f = open(data["path"], "rb")
    except:
        return 2

    return f


def readSend(f, sd, addr):
    while True:
        data = {}
        data["data"] = f.read(MAXSIZE)
        sendReturn = packet.send(sd, data, addr, packet.DATA)
        recvReturn = packet.recv(sd, packet.DATA_ACK, 3.0)

        if None in [sendReturn, recvReturn]:
            return True

        if len(data["data"]) != MAXSIZE:
            break


def run(sd, conn, srv):
    addr = conn[1]
    data = packet.get(conn[0], packet.CONNECT)

    f = checkConnData(data)

    if type(f) == int:
        return sendErr(sd, f, addr)

    size = os.path.getsize(data["path"])

    if not packet.send(sd, {"size": size}, addr, packet.CONNECT_ACK):
        return

    if readSend(f, sd, addr):
        return

    packet.send(sd, None, addr, packet.SHUTDOWN)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请指定服务器操作(start|stop|restart|statu)")
    else:
        udp.srvDaemon(9000, run, sys.argv[1])
