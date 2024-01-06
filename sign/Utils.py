from hashlib import md5
import base64


def toBit(data):
    data_bit = []
    for i in range(len(data)):
        xor_data = 0x80
        for j in range(8):
            data_bit.append(0 if (ord(data[i]) & xor_data) == 0 else 1)
            xor_data >>= 1
    return data_bit


def toBytes(data):
    arr1 = []
    for i in range(0, len(data), 8):
        tmp = 0
        for j in range(8):
            tmp <<= 1
            tmp |= data[i + j]
        arr1.append(tmp)
    return bytes(arr1)


def hash(data):
    md = md5()
    md.update(base64.b64encode(data))
    return md.hexdigest()
