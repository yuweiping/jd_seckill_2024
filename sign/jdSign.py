from random import randint
import time

from Utils import *
from TenMagic32 import TenMagic32
from TenMagic16 import TenMagic16
from TenSeattos import TenSeattos


def encrypt(data, data_len, encryptId, offset):
    encryptType = [0, 1, 2][offset:] + [0, 1, 2][0:offset]
    encrypt = encryptType[encryptId]
    switcher = {
        0: TenMagic32,
        1: TenMagic16,
        2: TenSeattos
    }

    return switcher[encrypt](data, data_len)


def getSign(functionId, body, uuid, client, clientVersion):
    t = time.time()
    st = str(int(round(t * 1000)))
    encryptId = randint(0, 2)
    offset = randint(0, 2)
    sv = "1" + str(offset) + str(encryptId)
    data = "&".join(("functionId=" + functionId, "body=" + body, "uuid=" + uuid, "client=" + client,
                     "clientVersion=" + clientVersion, "st=" + st, "sv=" + sv))
    sign = hash(encrypt(data, len(data), encryptId, offset))
    return sign


def getSignWithstv(functionId, body, uuid, client, clientVersion):
    t = time.time()
    st = str(int(round(t * 1000)))
    encryptId = randint(0, 2)
    offset = randint(0, 2)
    sv = "1" + str(offset) + str(encryptId)
    data = "&".join(("functionId=" + functionId, "body=" + body, "uuid=" + uuid, "client=" + client,
                     "clientVersion=" + clientVersion, "st=" + st, "sv=" + sv))
    sign = hash(encrypt(data, len(data), encryptId, offset))
    return "st=" + st + "&sign=" + sign + "&sv=" + sv


# test
'''
def main():
    functionId = "switchQuery"
    clientVersion = "11.8.3"
    client = "android"
    uuid = "YWC5Y2HuDNOnEWY0DWC0ZG=="
    body = "aaaa"
    Sign(functionId, body, uuid, client, clientVersion)
if __name__ == "__main__":
    main()
'''
