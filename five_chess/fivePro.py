#!/usr/bin/env python3

import pygame as pg

#  格子大小
SIZE = 30
#  缓冲画布规格
WIDE, HIGH = 1200, 900
#  横向/纵向最多可落子数
MAX = HIGH // SIZE - 1
#  敌方棋子颜色
ENEMY = (0, 0, 0)
#  己方棋子颜色
OWN = (255, 255, 255)
#  控子颜色
RED = (168, 0, 0)
#  棋盘颜色
BOARD = (168, 100, 0)
#  棋盘线颜色
LINE = (0, 0, 0)
#  连子方向列表
DIRECTION = [(0, 1), (1, 0), (1, 1), (-1, 1)]

class Game:
    def __init__(self):
        self.chess = []
        self.ctrl = (MAX // 2, MAX // 2)
        self.enemy = []
        self.own = []
        self.win = {"enemy": False, "own": False, "draw": False}

    def chessInit(self):
        for x in range(1, MAX + 1):
            for y in range(1, MAX + 1):
                self.chess.append((x, y))

    def changeCtrl(self, point):
        self.ctrl = point

    def chessAdd(self, point, op=0):
        if op == 0:
            self.enemy.append(point)
        else:
            self.own.append(point)

    def chessDel(self, point):
        self.chess.remove(point)


def pointTrans(point):
    return (point[0] * SIZE, point[1] * SIZE)


def printText(s, point, color=(0, 0, 0), size=SIZE):
    SCREEN = pg.display.get_surface()
    ft = pg.font.SysFont("arplumingtw", size)
    img = ft.render(s, True, color, BOARD)
    SCREEN.blit(img, pointTrans(point))


def drawLine(start, stop, trans=False):
    SCREEN = pg.display.get_surface()
    if trans:
        pg.draw.line(SCREEN, LINE, pointTrans(start), pointTrans(stop))
    else:
        pg.draw.line(SCREEN, LINE, start, stop)


def drawBoard(op=0):
    SCREEN = pg.display.get_surface()
    SCREEN.fill(BOARD)

    for i in range(1, MAX + 1):
        drawLine((1, i), (MAX, i), True)
        drawLine((i, 1), (i, MAX), True)

    printText("高手对决之五子棋", (MAX + 1, 1))
    side = ["敌方落子", "己方落子"][op]
    printText(side, (MAX + 3, 3))


def drawChess(color, point, r):
    SCREEN = pg.display.get_surface()
    pg.draw.circle(SCREEN, color, pointTrans(point), r)


def init(op=0):
    game = Game()
    game.chessInit()
    drawBoard(op)
    drawChess(RED, game.ctrl, SIZE // 4)
    pg.display.update()

    return game


def flash(point):
    drawChess(BOARD, point, SIZE // 4)

    pt = pointTrans(point)

    if point[0] > 1:
        drawLine((pt[0] - SIZE // 4, pt[1]), pt)
    if point[0] < MAX:
        drawLine((pt[0] + SIZE // 4, pt[1]), pt)
    if point[1] > 1:
        drawLine((pt[0], pt[1] - SIZE // 4), pt)
    if point[1] < MAX:
        drawLine((pt[0], pt[1] + SIZE // 4), pt)


def move(key, game):
    point = [game.ctrl[0], game.ctrl[1]]
    if key == pg.K_a and point[0] > 1 :
        point[0] -= 1
    elif key == pg.K_d and point[0] < MAX:
        point[0] += 1
    elif key == pg.K_s and point[1] < MAX:
        point[1] += 1
    elif key == pg.K_w and point[1] > 1:
        point[1] -= 1

    if game.ctrl not in game.chess:
        color = [ENEMY, OWN][game.ctrl in game.own]
        drawChess(color, game.ctrl, SIZE // 4)
    else:
        flash(game.ctrl)

    game.changeCtrl((point[0], point[1]))

    drawChess(RED, game.ctrl, SIZE // 4)


def fall(game, op=0):
    color = [ENEMY, OWN][op]
    game.chessAdd(game.ctrl, op)
    drawChess(color, game.ctrl, SIZE // 2)
    drawChess(RED, game.ctrl, SIZE // 4)
    game.chessDel(game.ctrl)
    if op:
        printText("敌方落子", (MAX + 3, 3))
    else:
        printText("己方落子", (MAX + 3, 3))


def traverse(x, y, chess):
    """
    落子后单个方向的相连棋子累计
    """
    n = 1
    while (chess[-1][0] + x * n, chess[-1][1] + y * n) in chess:
        n += 1
    m = 1
    while (chess[-1][0] - x * m, chess[-1][1] - y * m) in chess:
        n += 1
        m += 1

    return n


def scan(game, op=0):
    """
    落子后判断游戏是否结束
    """
    chess = [game.enemy, game.own][op]

    for x, y in DIRECTION:
        if traverse(x, y, chess) >= 5:
            return True


def over(game):
    if game.win["enemy"]:
        printText("敌方获胜", (MAX + 3, 3))
    elif game.win["own"]:
        printText("己方获胜", (MAX + 3, 3))
    elif game.win["draw"]:
        printText("双方平手", (MAX + 3, 3))

