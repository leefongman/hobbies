#!/usr/bin/env python3

import socket
from fivePlay import *
from vt100 import *


class FiveChessServer(FivePlay):
    def __init__(self, sd, addr):
        self.sd = sd
        self.addr = addr
        self.isRecv = True

    def search(self):
        self.sd.bind(addr)
        print(SCREEN + goto(1, 1), end="", flush=True)
        print("正在等待敌方连接......")
        self.addr = self.sd.recvfrom(1024)[1]
        self.sd.close()
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sd.sendto("开始游戏".encode(), self.addr)
        print("开始游戏")
        self.isRecv = False

    def pro(self, game):
        while True:
            flag = self.wait(game)
            if flag == False:
                break
            elif flag:
                game = init(1)

            flag = self.fall(game)
            if flag == False:
                break
            elif flag:
                game = init()

        self.sd.close()
        pg.quit()

    def handle(self):
        pg.display.set_mode((WIDE, HIGH))
        pg.init()
        game = init(1)
        self.pro(game)

if __name__ == "__main__":
    addr = ("0.0.0.0", 9000)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server = FiveChessServer(sd, addr)
    server.search()
    server.handle()

