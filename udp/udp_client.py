#!/usr/bin/env python3

import signal
import socket
from file_transferation import *
from vt100 import *

class UdpClient:
    def __init__(self, sd, ip, port):
        self.sd = sd
        self.ip = ip
        self.port = port

    def handle(self):
        addr = (self.ip, self.port)
        while True:
            print(SCREEN + goto(1, 1), end="", flush=True)
            print("服务器地址:", addr)
            username = input("用户名: ")
            password = input("密码: ")
            self.sd.sendto((username + " " + password).encode(), addr)
            if self.sd.recvfrom(4096)[0].decode() == "ok":
                break

        while True:
            print(goto(4, 1) + LINE, end="", flush=True)
            req = input("输入请求: ")
            if req == "exit" or not req:
                self.sd.sendto("exit".encode(), addr)
                break

            self.sd.sendto(req.encode(), addr)
            req = req.split()
            op = "None"

            if len(req) == 2:
                op, filename = req

            if op == "put":
                send(self.sd, filename, addr)
            elif op == "get":
                recv(self.sd, filename, addr)
            else:
                print(self.sd.recvfrom(4096)[0].decode() + "\n" + SAVE,
                        end="", flush=True)

        print(LOAD, end="", flush=True)


if __name__ == "__main__":
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    ip, port = "0.0.0.0", 9000
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client = UdpClient(sd, ip, port)
    client.handle()
    sd.close()

