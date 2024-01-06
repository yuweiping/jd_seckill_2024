from Utils import *


def TenSeattos(data, data_len):
    key = "80306f4370b39fd5630ad0529f77adb6"
    meta_data = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0x0F, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
    arr = [0] * data_len
    for i in range(data_len):
        arr[i] = ord(data[i])
        arr[i] ^= ord(key[i & 7]) ^ meta_data[i & 0xf]
        arr[i] += meta_data[i & 0xf]
        arr[i] &= 0xff
        arr[i] ^= meta_data[i & 0xf]
        arr[i] ^= ord(key[i & 7])
    return bytes(arr)
