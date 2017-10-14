#!/usr/bin/env python3

import socket
from fivePlay import *
from vt100 import *


class FiveChessClient(FivePlay):
    def __init__(self, sd, addr):
        self.sd = sd
        self.addr = addr

    def connect(self):
        print(SCREEN + goto(1, 1), end="", flush=True)
        print("正在请求连接......")
        self.sd.sendto("请求连接......".encode(), self.addr)
        data, self.addr = self.sd.recvfrom(4096)
        print(data.decode())
        self.isRecv = True

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
        game = init()
        self.pro(game)

if __name__ == "__main__":
    addr = ("3.3.3.117", 9000)
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server = FiveChessClient(sd, addr)
    server.connect()
    server.handle()

