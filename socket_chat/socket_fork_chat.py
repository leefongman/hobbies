#!/usr/bin/env python3

import socket
import os
import signal
import sys
from vt100 import *

recvList = []


def ptRecv(sd, name="Server"):
    global recvList

    content, addr = sd.recvfrom(1024)
    content = content.decode()
    if content == "exit":
        print()
        return

    s = "%s receive from %s: %s" % (name, addr[0], content)
    recvList.append(s)
    length = len(recvList)
    start = length - 10 if length >= 10 else 0
    for idx in range(start, length):
        row = idx - start + 1
        print(SAVE + goto(row, 1) + LINE + recvList[idx] + LOAD,
                end="", flush=True)

    return addr


def myExit(sig, stack):
    os._exit(0)


def chat(sd, addr, name="Server"):
    if os.fork() == 0:
        while ptRecv(sd, name):
            pass
    else:
        while True:
            s = "%s send to: " % name
            content = input(goto(13, 1) + LINE + s)
            sd.sendto(content.encode(), addr)
            if content == "exit":
                break

    sd.close()
    os.kill(0, signal.SIGTERM)


def main(argv):

    argc = len(argv)

    port = int(argv[1]) if argc > 1 else 9000
    isSrv = True if argc < 3 else False
    name = "Server" if isSrv else "Common"
    ip = argv[2] if argc == 3 else "0.0.0.0"

    print(SCREEN, end="", flush=True)
    signal.signal(signal.SIGTERM, myExit)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    addr = (ip, port)
    if isSrv:
        sd.bind(addr)
        print(goto(1, 1) + LINE + "waiting...", end="", flush=True)
        _, addr = sd.recvfrom(1024)
        sd.close()
        sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sd.sendto("connected".encode(), addr)
    else:
        sd.sendto("connecting".encode(), addr)
        _, addr = sd.recvfrom(1024)

    chat(sd, addr, name)


if __name__ == "__main__":
    main(sys.argv)
