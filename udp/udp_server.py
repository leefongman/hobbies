#!/usr/bin/env python3

import socket
import signal
from file_transferation import *
from vt100 import *


class UdpServer:
    def __init__(self, sd, ip, port):
        self.sd = sd
        self.ip = ip
        self.port = port
        self.sd.bind((ip, port))

    def handle(self):
        while True:
            print(SCREEN + goto(1, 1), end="", flush=True)
            print("正在等待客户端连接......")
            user, addr = self.sd.recvfrom(4096)
            user = user.decode().split()
            if len(user) == 2 and user[0] in USER:
                if USER[user[0]] == user[1]:
                    sd.sendto("ok".encode(), addr)
                    break
            sd.sendto("用户名或密码错误......".encode(), addr)

        print("已连接的客户端:", addr)
        while True:
            data = self.sd.recvfrom(4096)[0]
            data = data.decode()
            if data == "exit":
                print("客户端已断开连接")
                break

            data = data.split()
            op = "None"
            if len(data) == 2:
                op, filename = data

            if op == "put":
                recv(self.sd, filename, addr)
            elif op == "get":
                send(self.sd, filename, addr)
            else:
                self.sd.sendto("请求有误......".encode(), addr)


if __name__ == "__main__":
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    ip, port = "0.0.0.0", 9000
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server = UdpServer(sd, ip, port)
    server.handle()
    sd.close()

