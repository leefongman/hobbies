#!/usr/bin/env python3

import socket
import threading
import signal
import os
import datetime
import packet

def nowTime():
    """
    获取当前日期时间
    """
    return datetime.datetime.now().strftime("%F %T")


def getName(kargs):
    if "name" not in kargs:
        kargs["name"] = "srv"

    return kargs["name"]


def getSrvPid(name):
    try:
        return int(open("/tmp/%s.pid" % name).read())
    except:
        return


def srvIsAlive(name):
    pid = getSrvPid(name)

    if pid and os.path.exists("/proc/%d" % pid):
        return pid

    return

def createSocket(srv):
    """
    创建套接字
    """
    srv["sd"] = socket.socket(type=socket.SOCK_DGRAM)
    srv["sd"].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv["sd"].bind(srv["addr"])


def connect(srv):
    t = threading.currentThread()
    print("[%s]%s connect start" % (nowTime(), t))

    while not srv["close"]:
        connMes = srv["sd"].recvfrom(srv["recvmax"])

        if not connMes[0]:
            break

        print("[%s]connect: " % nowTime(), connMes)

        cliSd = socket.socket(type=socket.SOCK_DGRAM)
        srv["call"](cliSd, connMes, srv)
        cliSd.close

        print("[%s]connected: " % nowTime(), connMes)

    print("[%s]%s connect exit" % (nowTime(), t))


def createThreads(srv, call):
    """
    创建工作线程
    """
    srv["threads"] = []

    for i in range(srv["climax"]):
        srv["threads"].append(threading.Thread(target=call, args=(srv, )))


def writePid(srv):
    """
    记录进程id
    """
    name = getName(srv)
    f = open("/tmp/%s.pid" % name, 'w')
    f.write(str(os.getpid()))
    f.close()


def createSrv(addr, call, **kargs):
    """
    创建udp服务器
    """
    if not callable(call):
        return

    srv = {}
    srv["args"] = None
    srv["recvmax"] = 1024
    srv["climax"] = 5
    srv["close"] = False
    srv["daemon"] = False
    srv.update(kargs)
    srv["addr"] = addr if type(addr) == tuple else ("0.0.0.0", addr)
    srv["call"] = call
    createSocket(srv)
    createThreads(srv, connect)
    writePid(srv)

    print("[%s]srv start..." % nowTime())

    return srv


def srvStart(srv):
    for t in srv["threads"]:
        t.start()


def srvClose(srv):
    srv["close"] = True
    try:
        srv["sd"].shutdown(socket.SHUT_RDWR)
    except:
        pass

    srv["sd"].close()



def srvJoin(srv):
    for t in srv["threads"]:
        t.join()


def start(port, call, kargs, re=False):
    """
    启动服务器
    """
    def srvExit(sig, info):
        srvClose(srv)

    if srvIsAlive(kargs["name"]) and not re:
        return

    if os.fork() == 0:
        os.setsid()

        f = open("/tmp/%s.log" % kargs["name"], 'a')
        os.dup2(f.fileno(), 1)

        srv = createSrv(port, call, **kargs)
        signal.signal(signal.SIGUSR1, srvExit)
        srvStart(srv)
        srvJoin(srv)


def stop(kargs):
    """
    关闭服务器
    """
    pid = srvIsAlive(kargs["name"])

    if not pid:
        return

    os.kill(pid, signal.SIGUSR1)


def restart(port, call, kargs):
    """
    重启服务器
    """
    stop(kargs)
    start(port, call, kargs, True)


def srvDaemon(port, call, cmd="start", **kargs):
    getName(kargs)

    if cmd == "start":
        start(port, call, kargs)
    elif cmd == "restart":
        restart(port, call, kargs)
    elif cmd == "stop":
        stop(kargs)
    elif cmd == "statu":
        pid = srvIsAlive(kargs["name"])
        if pid:
            print("%s(%d) 服务器已经启动...." % (kargs['name'], pid))
        else:
            print("%s 服务器未启动" % kargs['name'])



def createCli(addr, connData):
    sd = socket.socket(type=socket.SOCK_DGRAM)
    if not packet.send(sd, connData, addr, packet.CONNECT):
        sd.close()
        return

    return sd

