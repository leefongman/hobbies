#!/usr/bin/env python3

import pickle

"""
数据包类型常量声明
"""
#  连接请求包
CONNECT = 1
#  错误包
ERROR = 2
#  连接成功包
CONNECT_ACK = 3
#  数据包
DATA = 4
#  回应包
DATA_ACK = 5
#  断开连接包
SHUTDOWN = 6

#  每个数据包的最大长度
MAXSIZE = 1024

#  错误信息字典
ERRORMES = {
        0: "用户名不存在",
        1: "密码错误",
        2: "文件不存在",
        3: "非法数据包"
        }


def get(data, tp=0):
    #  数据反序列化
    d = pickle.loads(data)

    if type(d) == dict and "type" in d and (tp == 0 or d["type"] == tp):
        #  满足条件时返回字典对象
        return d


def put(data, tp):
    #  初始化需要返回的待序列化字典
    d = {}
    if data and type(data) != dict:
        #  非字典数据字典化
        d["data"] = data
    elif data:
        d = data

    d["type"] = tp

    return pickle.dumps(d)


def send(sd, data, addr, tp):
    #  将需要发送的数据字典化并序列化
    sendData = put(data, tp)
    length = len(sendData)

    return length if sd.sendto(sendData, addr) == length else None


def recv(sd, tp=0, timeout=None):
    #  设置超时
    sd.settimeout(timeout)

    try:
        data, addr = sd.recvfrom(MAXSIZE)
    except:
        return
    finally:
        sd.settimeout(None)

    recvData = get(data, tp)

    return (recvData, addr) if recvData else None

