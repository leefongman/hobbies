#!/usr/bin/env python3

import pygame as pg


class Pt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, val):
        return Pt(self.x * val, self.y * val)

    def __add__(self, val):
        if type(val) == int:
            return Pt(self.x + val, self.y + val)

        if isinstance(val, Pt):
            return Pt(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return self + (val * (-1))

    def cp(self):
        return Pt(self.x, self.y)

    def get(self):
        return (self.x, self.y)

    def move(self, x, y):
        self.x += x
        self.y += y


class Rook:
    """
    車类
    """
    def rook(self):
        return not self.prepCount()


class Knight:
    """
    马类
    """
    def knight(self):
        pdxy = self.cursor - self.select

        if abs(pdxy.x * pdxy.y) != 2:
            return False

        return self.prepStop()


class Elephant:
    """
    相象类
    """
    def elephant(self):
        pdxy = self.cursor - self.select

        if abs(pdxy.x) != 2 or abs(pdxy.y) != 2:
            return False

        return self.prepStop()


class Mandarin:
    """
    士类
    """
    def mandarin(self):
        pdxy = self.cursor - self.select

        if abs(pdxy.x * pdxy.y) != 1:
            return False

        return self.prepRange()


class King:
    """
    將帥类
    """
    def king(self):
        pdxy = self.cursor - self.select

        if abs(pdxy.x) + abs(pdxy.y) != 1:
            return False

        return self.prepRange()


class Pawn:
    """
    兵卒类
    """
    def pawn(self):
        pdxy = self.cursor - self.select
        flag = 1 if self.isRed else -1

        if abs(pdxy.x) + abs(pdxy.y) != 1 or flag * pdxy.y < 0:
            return False

        st, sp = (0, 4) if self.isRed else (5, 9)

        if abs(pdxy.x) == 1 and st <= self.select.y <= sp:
            return False

        return True


class Cannon:
    """
    炮类
    """
    def cannon(self):
        if not self.prepCount() and self.cursor.get() not in self.getEnemy():
            return True

        if self.prepCount() == 1 and self.cursor.get() in self.getEnemy():
            return True

        return False


class Chess(Rook, Knight, Elephant, Mandarin, King, Pawn, Cannon):
    def __init__(self, size):
        self.size = size  # 棋盘单元格边长的像素尺寸
        self.across = 9  # 棋盘横向最多可落子数
        self.stand = 10  # 棋盘纵向最多可落子数
        self.select = None  # 已选定棋子坐标位置
        self.isRed = True  # 是否为红方落子
        self.wayInit()
        self.pgInit()
        self.gameInit()

    def prepCount(self):
        """
        判断車炮是否正确移动的预处理
        """
        sx, sy = self.select.get()
        cx, cy = self.cursor.get()

        if sx != cx and sy != cy:
            return 2

        dx = (cx - sx) // abs(cx - sx) if cx - sx else 0
        dy = (cy - sy) // abs(cy - sy) if cy - sy else 0
        dt = abs(cx - sx) if cx - sx else abs(cy - sy)
        count = 0

        for d in range(1, dt):
            pt = (sx + dx * d, sy + dy * d)
            count += pt in self.red or pt in self.black

        return count

    def prepStop(self):
        """
        判断马相象移动的方向有无阻塞
        """
        pt = self.cursor + self.select
        pt = (pt.x // 2, pt.y // 2)

        if pt in self.red or pt in self.black:
            return False

        return True

    def prepRange(self):
        x, y = self.cursor.get()
        st, sp = (0, 2) if self.isRed else (7, 9)

        if not(3 <= x <= 5 and st <= y <= sp):
            return False

        return True

    def wayInit(self):
        """
        棋子走法初始化
        """
        kinds = ["車", "馬", "相", "象", "士", "帥", "將", "炮", "兵", "卒"]
        funcs = [self.rook, self.knight, self.elephant, self.elephant,
                self.mandarin, self.king, self.king, self.cannon,
                self.pawn, self.pawn]

        way = {}
        for key, val in zip(kinds, funcs):
            way[key] = val

        self.way = way


    def pgInit(self):
        """
        pygame初始化
        """
        pg.init()
        self.screen = pg.display.set_mode((self.size * 12, self.size * 13))

    def posInit(self):
        """
        初始化红黑双方棋子位置
        """
        red = {}  # 红方所有棋子
        black = {}  # 黑方所有棋子
        kinds = ["車", "馬", "相", "士", "帥", "炮", "兵"]

        for idx, kind in enumerate(kinds):
            if idx < 5:
                red[(idx, 0)] = red[(8 - idx, 0)] = kind
                black[(idx, 9)] = black[(8 - idx, 9)] = kind
            elif idx == 5:
                red[(1, 2)] = red[(7, 2)] = kind
                black[(1, 7)] = black[(7, 7)] = kind
            else:
                for x in range(0, 9, 2):
                    red[(x, 3)] = kind
                    black[(x, 6)] = "卒"
            black[(2, 9)] = black[(6, 9)] = "象"
            black[(4, 9)] =  "將"

        self.red, self.black = red, black

    def pter(self, tup):
        """
        点类转化器
        """
        return Pt(tup[0], tup[1])

    def gameInit(self):
        self.cursor = Pt(0, 0)  # 棋子选择器
        self.win = {"red": False, "black": False}
        self.posInit()

    def txt(self, s, pt, color):
        """
        显示中文文本
        """
        font = pg.font.SysFont("arplumingtw", self.size // 2)
        font.set_bold(True)
        img = font.render(s, False, color)
        self.screen.blit(img, (pt * self.size - self.size // 4).get())

    def real(self, pt):
        return (pt + 2) * self.size

    def line(self, start, stop, isReal=False):
        """
        棋盘上画线
        """
        if not isReal:
            start, stop = self.real(start), self.real(stop)

        pg.draw.line(self.screen, (200, 0, 0), start.get(), stop.get())

    def circle(self, pt):
        """
        棋子尺寸的圆
        """
        pg.draw.circle(self.screen, (255, 195, 135),pt.get(), self.size // 2)

    def angle(self, pt, left=True):
        """
        棋盘炮/兵/卒初始位置上的直角
        """
        dst = self.size // 10 * [-1, 1][left]
        dsp = self.size // 3 * [-1, 1][left]
        p = self.real(pt)

        for sign in [1, -1]:
            self.line(p - Pt(dst, dst * sign), p - Pt(dst, dsp * sign), True)
            self.line(p - Pt(dst, dst * sign), p - Pt(dsp, dst * sign), True)

    def bg(self):
        self.screen.fill((130, 40, 50))

    def gameBg(self):
        self.screen.fill((170, 110, 50), (self.size, self.size,
            self.size * 10, self.size * 11))

    def decorate(self):
        """
        棋盘装饰
        """
        #  横线
        for row in range(self.stand):
            self.line(Pt(0, row), Pt(self.across - 1, row))
        #  竖线
        for col in range(self.across):
            if 0 < col < self.across - 1:
                self.line(Pt(col, 0), Pt(col, 4))
                self.line(Pt(col, 5), Pt(col, self.stand - 1))
            else:
                self.line(Pt(col, 0), Pt(col, self.stand - 1))
        #  炮角
        for row, col in [(2, 1), (2, 7), (7, 1), (7, 7)]:
            self.angle(Pt(col, row))
            self.angle(Pt(col, row), False)
        #  兵卒角
        for row in [3, 6]:
            for col in range(0, 8, 2):
                self.angle(Pt(col, row), False)
            for col in range(2, 9, 2):
                self.angle(Pt(col, row))
        #  斜线
        for st, sp in [(0, 2), (2, 0), (7, 9), (9, 7)]:
            self.line(Pt(3, st), Pt(5, sp))

    def chess(self, pt, value, color):
        """
        单个棋子
        """
        self.circle(self.real(pt))
        self.txt(value, pt + 2, color)


    def side(self, pts, color):
        """
        一方棋子
        """
        for key, value in pts.items():
            self.chess(self.pter(key), value, color)


    def sides(self):
        """
        双方棋子
        """
        #  红方棋子
        self.side(self.red, (200, 0, 0))
        #  黑方棋子
        self.side(self.black, (0, 0, 0))

    def pt2rect(self, pt):
        """
        生成区域
        """
        p = self.real(pt) - self.size // 2
        return (p.x, p.y, self.size, self.size)

    def sel(self, pt, color):
        """
        玩家控制用方框
        """
        pg.draw.rect(self.screen, color, self.pt2rect(pt), 2)

    def cur(self):
        """
        已选光标和当前光标
        """
        #  当前光标
        self.sel(self.cursor, (200, 200, 200))
        #  已选光标
        if self.select:
            self.sel(self.select, (0, 0, 200))

    def flush(self):
        """
        棋盘更新
        """
        self.bg()
        self.gameBg()
        self.decorate()
        self.sides()
        self.cur()
        #  结果打印
        if self.win["red"] or self.win["black"]:
            left = "红黑"[self.win["black"]]
            self.txt(left + "方胜 按空格重开", Pt(1.5, 0.5), (255, 255, 255))
        #  提示落子方
        turn = "黑红"[self.isRed]
        self.txt(turn + "方落子", Pt(9, 0.5), (255, 255, 255))

        pg.display.update()

    def getSelf(self):
        """
        获得己方棋子字典
        """
        return self.red if self.isRed else self.black

    def getEnemy(self):
        """
        获得敌方棋子字典
        """
        return self.red if not self.isRed else self.black

    def result(self):
        """
        判断已决出胜负时的数据更新
        """
        self.win["red"] = True if self.isRed else False
        self.win["black"] = False if self.isRed else True


    def isMe(self):
        """
        判断要落子的位置有无己方棋子
        """
        return self.cursor.get() in self.getSelf()

    def correct(self):
        """
        判断走法是否正确
        """

        key = self.getSelf()[self.select.get()]
        return self.way[key]()

    def gameExit(self):
        """
        退出游戏
        """
        pg.quit()
        exit()

    def move(self, e):
        """
        移动棋子选择器
        """
        if e.key == pg.K_LEFT and self.cursor.x > 0:
            self.cursor.move(-1, 0)
        elif e.key == pg.K_RIGHT and self.cursor.x < self.across - 1:
            self.cursor.move(1, 0)
        elif e.key == pg.K_UP and self.cursor.y > 0:
            self.cursor.move(0, -1)
        elif e.key == pg.K_DOWN and self.cursor.y < self.stand - 1:
            self.cursor.move(0, 1)

    def scan(self):
        """
        吃子操作
        """
        pts = self.getEnemy()

        if self.cursor.get() in pts:
            if pts[self.cursor.get()] in "將帥":
                #  敌方主公被吃,更新胜负结果
                self.result()
            #  敌方去除被吃棋子
            del pts[self.cursor.get()]

    def special(self):
        """
        判断是否出现特殊情况,將帥对峙
        """
        #  获取红方"帥"所在位置
        for key, val in self.red.items():
            if val == "帥":
                break
        x, y = key
        for y in range(y + 1, self.stand):
            #  有己方棋子挡在前方,没有出现將帥对峙
            if (x, y) in self.red:
                return
            if (x, y) in self.black:
                break
        #  正前方为黑方"將",决出胜负
        if self.black[(x, y)] == "將":
            self.result()

    def fall(self):
        """
        落子
        """
        pts = self.getSelf()
        pts[self.cursor.get()] = pts[self.select.get()]
        del pts[self.select.get()]
        self.select = None
        self.isRed = not self.isRed

    def canSel(self):
        """
        判断待选定位置是否可被选定,并更新
        """
        if self.cursor.get() in self.getSelf():
            self.select = self.cursor.cp()

    def choose(self, e):
        """
        选定棋子和放弃选定
        """
        if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
            if self.select == None:
                self.canSel()
            elif not self.isMe() and self.correct():
                self.scan()
                self.fall()
                self.special()

    def giveUp(self, e):
        """
        投降
        """
        if e.key == pg.K_q:
            self.win["red"] = False if self.isRed else True
            self.win["black"] = True if self.isRed else False

    def back(self, e):
        """
        回退,放弃选定
        """
        if e.type == pg.KEYDOWN and e.key == pg.K_BACKSPACE:
            self.select = None

    def ctrl(self):
        """
        用户按键控制
        """
        while True:
            e = pg.event.wait()

            if e.type == pg.KEYDOWN:
                #  未分出胜负时的玩家操作
                if not self.win["red"] and not self.win["black"]:
                    self.move(e)
                    self.choose(e)
                    self.back(e)
                    self.giveUp(e)
                #  退出游戏
                elif e.key == pg.K_ESCAPE:
                    self.gameExit()
                #  重新开始
                elif e.key == pg.K_SPACE:
                    self.gameInit()

            self.flush()

    def run(self):
        self.flush()
        self.ctrl()


if __name__ == "__main__":
    Chess(60).run()
