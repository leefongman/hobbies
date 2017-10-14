#!/usr/bin/env python3

import os
import sys
import pygame as pg
import socket
import signal

#  格子大小
SIZE = 30
#  缓冲画布规格
WIDE, HIGH = 1200, 900
#  黑方棋子颜色
BLACK = (0, 0, 0)
#  白方棋子颜色
WHITE = (255, 255, 255)
#  控子颜色
RED = (168, 0, 0)
#  棋盘颜色
BOARD = (168, 100, 0)
#  棋盘线颜色
LINE = (0, 0, 0)
#  画布
SCREEN = pg.display.set_mode((WIDE, HIGH))
#  连子方向列表
DIRECTION = [(0, 1), (1, 0), (1, 1), (-1, 1)]


class Game:
    def __init__(self):
        self.chess = []
        self.ctrl = (HIGH // 2, HIGH // 2)
        self.black = []
        self.white = []
        self.player = "black"
        self.win = {"black": False, "white": False, "draw": False}

    def chessInit(self):
        for x in range(SIZE, HIGH, SIZE):
            for y in range(SIZE, HIGH, SIZE):
                self.chess.append((x, y))

    def swapPlayer(self):
        self.player = ["white", "black"][self.player == "white"]

    def changeCtrl(self, point):
        self.ctrl = point

    def chessAdd(self, point):
        if self.player == "black":
            self.black.append(point)
        else:
            self.white.append(point)

    def chessDel(self, point):
        self.chess.remove(point)


def printText(s, point, color=BLACK, size=SIZE):
    font = pg.font.SysFont("arplumingtw", size)
    img = font.render(s, True, color, BOARD)
    SCREEN.blit(img, point)


def drawBoard():
    SCREEN.fill(BOARD)

    for i in range(SIZE, HIGH, SIZE):
        pg.draw.line(SCREEN, LINE, (SIZE, i), (HIGH - SIZE, i))
        pg.draw.line(SCREEN, LINE, (i, SIZE), (i, HIGH - SIZE))

    printText("高手对决之五子棋", (HIGH, SIZE))
    printText("黑方落子", (HIGH + 2 * SIZE, 3 * SIZE))


def drawChess(color, point, r):
    pg.draw.circle(SCREEN, color, point, r)


def init():
    pg.init()
    game = Game()
    game.chessInit()
    drawBoard()
    drawChess(RED, game.ctrl, SIZE // 4)

    pg.display.update()

    return game


def flash(point):
    drawChess(BOARD, point, SIZE // 4)

    if point[0] > SIZE:
        pg.draw.line(SCREEN, LINE, (point[0] - SIZE // 4, point[1]), point)
    if point[0] < HIGH - SIZE:
        pg.draw.line(SCREEN, LINE, (point[0] + SIZE // 4, point[1]), point)
    if point[1] > SIZE:
        pg.draw.line(SCREEN, LINE, (point[0], point[1] - SIZE // 4), point)
    if point[1] < HIGH - SIZE:
        pg.draw.line(SCREEN, LINE, (point[0], point[1] + SIZE // 4), point)


def move(e, game):
    point = [game.ctrl[0], game.ctrl[1]]
    if e.key == pg.K_a and point[0] - SIZE >= SIZE:
        point[0] -= SIZE
    elif e.key == pg.K_d and point[0] + SIZE <= HIGH - SIZE:
        point[0] += SIZE
    elif e.key == pg.K_s and point[1] + SIZE <= HIGH - SIZE:
        point[1] += SIZE
    elif e.key == pg.K_w and point[1] - SIZE >= SIZE:
        point[1] -= SIZE

    if game.ctrl not in game.chess:
        color = [BLACK, WHITE][game.ctrl in game.white]
        drawChess(color, game.ctrl, SIZE // 4)
    else:
        flash(game.ctrl)

    game.changeCtrl((point[0], point[1]))

    drawChess(RED, game.ctrl, SIZE // 4)


def fall(game):
    color = [WHITE, BLACK][game.player == "black"]
    game.chessAdd(game.ctrl)
    scan(game)
    drawChess(color, game.ctrl, SIZE // 2)
    drawChess(RED, game.ctrl, SIZE // 4)
    game.chessDel(game.ctrl)
    game.swapPlayer()
    if color != BLACK:
        printText("黑方落子", (HIGH + 2 * SIZE, 3 * SIZE))
    else:
        printText("白方落子", (HIGH + 2 * SIZE, 3 * SIZE))


def traverse(x, y, chess):
    """
    落子后单个方向的相连棋子累计
    """
    n = 1
    while (chess[-1][0] + x * SIZE * n, chess[-1][1] + y * SIZE * n) in chess:
        n += 1
    m = 1
    while (chess[-1][0] - x * SIZE * m, chess[-1][1] - y * SIZE * m) in chess:
        n += 1
        m += 1

    return n


def scan(game):
    """
    落子后判断游戏是否结束
    """
    chess = [game.white, game.black][game.player == "black"]

    for x, y in DIRECTION:
        if traverse(x, y, chess) >= 5:
            game.win[game.player] = True


def over(game):
    if game.win["black"]:
        printText("黑方获胜", (HIGH + 2 * SIZE, 3 * SIZE))
        return True
    elif game.win["white"]:
        printText("白方获胜", (HIGH + 2 * SIZE, 3 * SIZE))
        return True
    elif game.win["draw"]:
        printText("双方平手", (HIGH + 2 * SIZE, 3 * SIZE))
        return True

def run():
    game = init()

    while True:
        e = pg.event.wait()

        if e.type == pg.QUIT:
            break
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                break
            elif e.key == pg.K_SPACE:
                game = init()

            if game.chess:
                if e.key in [pg.K_a, pg.K_d, pg.K_w, pg.K_s]:
                    move(e, game)
                elif e.key == pg.K_p and game.ctrl in game.chess:
                    fall(game)
            else:
                game.win["draw"] = True

            if over(game):
                game.chess = []

            pg.display.update()


if __name__ == "__main__":
    run()

