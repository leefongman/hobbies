from fivePro import *
import pygame as pg


class FivePlay():
    def __init__(self, sd, addr):
        self.sd = sd
        self.addr = addr
        self.isRecv = False

    def quit(self, e):
        if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.sd.sendto("quit".encode(), self.addr)

            return True

    def play(self, key, game):
        if key in [pg.K_a, pg.K_d, pg.K_w, pg.K_s]:
            move(key, game)
            pg.display.update()
        elif key == pg.K_p and game.ctrl in game.chess:
            self.send(game)
            self.isRecv = True

    def replay(self, key, game):
        if key == pg.K_SPACE:
            self.sd.sendto("replay".encode(), self.addr)
            self.isRecv = True

            return True

    def recv(self, game):
        data = self.sd.recvfrom(1024)[0].decode()

        if data == "replay":
            return True
        elif data == "quit":
            return False
        else:
            data = data[1: -1].split(", ")
            point = (int(data[0]), int(data[1]))
            if game.ctrl not in game.own:
                flash(game.ctrl)
            else:
                drawChess(OWN, game.ctrl, SIZE // 4)
            game.changeCtrl(point)
            fall(game)
            if scan(game):
                game.chess = []
                game.win["enemy"] = True
            elif not game.chess:
                game.win["draw"] = True
            over(game)

        pg.display.update()


    def send(self, game):
        fall(game, 1)
        self.sd.sendto(str(game.ctrl).encode(), self.addr)

        if scan(game, 1):
            game.win["own"] = True
            game.chess = []
        elif not game.chess:
            game.win["draw"] = True
        over(game)
        pg.display.update()

    def wait(self, game):
        if self.isRecv:
            self.isRecv = False

            return self.recv(game)

    def fall(self, game):
        if not self.isRecv:
            e = pg.event.wait()
            if e.type == pg.KEYDOWN and game.chess:
                self.play(e.key, game)
            elif e.type == pg.KEYDOWN and not game.chess:
                if self.quit(e):
                    return False
                elif self.replay(e.key, game):
                    return True

