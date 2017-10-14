#  文件传输处理函数封装

USER = {"lee": "123", "tom": "456", "mary": "789"}

def recv(sd, filename, addr):
    """
    文件接收处理函数
    """
    print("开始接收文件......")
    f = open("copy_" + filename, "wb")
    sd.sendto("准备就绪......".encode(), addr)

    while True:
        data = sd.recvfrom(4096)[0]

        if not data:
            print("文件接收完毕")
            break

        f.write(data)
        sd.sendto("ok".encode(), addr)
    f.close()


def send(sd, filename, addr):
    """
    文件发送处理函数
    """
    print("开始发送文件......")
    f = open(filename, "rb")
    while True:
        data = f.read(4096)
        sd.sendto(data, addr)

        if not data:
            break

        sd.recvfrom(4096)
    f.close()
    print("文件发送完毕")
