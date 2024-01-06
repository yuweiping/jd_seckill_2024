#!/usr/bin/env python
# -*- encoding=utf8 -*-

import json
import random
import time
from datetime import datetime
from urllib import parse
import requests


def response_status(resp):
    if resp.status_code != requests.codes.OK:
        print('Status: %u, Url: %s' % (resp.status_code, resp.url))
        return False
    return True


def wait_some_time():
    time.sleep(random.randint(100, 300) / 1000)


def local_time():
    """
    获取本地时间戳
    """
    local_timestamp = round(time.time() * 1000)
    # print(local_timestamp)
    return local_timestamp


def format_time(local_timestamp, time_format):
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(local_timestamp / 1000.0)
    # 格式化输出为时间字符串
    formatted_time = dt_object.strftime(time_format)
    # 如果时间格式包含毫秒（%f），则只保留3位小数
    if '%f' in time_format:
        formatted_time = formatted_time[:-3]
    return formatted_time

def TDEncrypt(m):
    m = json.dumps(m, separators=(',', ':'))
    m = parse.quote_plus(m)
    n = ""
    g = 0
    s64 = "23IL<N01c7KvwZO56RSTAfghiFyzWJqVabGH4PQdopUrsCuX*xeBjkltDEmn89.-"
    m_l = len(m)
    while g < m_l:
        f = ord(m[g])
        g += 1
        d = ord(m[g]) if g < m_l else 0
        g += 1
        a = ord(m[g]) if g < m_l else 0
        g += 1
        b = f >> 2
        f = (f & 3) << 4 | d >> 4
        e = (d & 15) << 2 | a >> 6
        c = a & 63
        if d == 0:
            e = c = 64
        elif a == 0:
            c = 64

        if b < 64:
            n += s64[b]
        if f < 64:
            n += s64[f]
        if e < 64:
            n += s64[e]
        if c < 64:
            n += s64[c]
    # print(n)
    return n + "/"


# jd 的base64加密
def encode_base64(arr):
    f42237a = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'U',
               'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'e', 'f',
               'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+',
               '/']

    result = ""
    for i in range(0, len(arr), 3):
        arr2 = [0] * 4
        b = 0
        for i2 in range(3):
            i3 = i + i2
            if i3 <= len(arr) - 1:
                arr2[i2] = (b | ((arr[i3] & 255) >> ((i2 * 2) + 2))) & 255
                b = (((arr[i3] & 255) << (((2 - i2) * 2) + 2)) & 255) >> 2
            else:
                arr2[i2] = b
                b = 0x40
        arr2[3] = b
        for i4 in range(4):
            result += f42237a[arr2[i4]] if arr2[i4] <= 63 else '='
    return result


def decode_base64(input_str):
    f40555a = ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'U',
               'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'e', 'f',
               'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+',
               '/']
    input_str = input_str.replace("=", "")
    input_bytes = input_str.encode()
    bArr = bytearray()
    for i in range(len(input_bytes)):
        char = input_bytes[i:i + 1].decode()
        bArr.append(f40555a.index(char))

    output = bytearray()
    i = 0
    while i < len(bArr):
        bArr2 = bytearray()
        i4 = 0
        for i5 in range(3):
            i6 = i + i5
            i7 = i6 + 1
            if i7 < len(bArr) and bArr[i7] >= 0:
                bArr2.append(((bArr[i6] & 255) << ((i5 * 2) + 2) & 255) | (bArr[i7] & 255) >> ((2 - (i5 + 1)) * 2 + 2))
                i4 += 1

        output.extend(bArr2[:i4])
        i += 4

    return bytes(output).decode()


# 根据给定的时间返回今天这个时间的时间戳
def str2timestamp(time_str):
    today = datetime.now().date()
    time_format = '%H:%M:%S.%f'
    time_object = datetime.strptime(time_str, time_format).time()
    # 合并日期和时间
    target_datetime = datetime.combine(today, time_object)
    # 获取时间戳（以秒为单位）
    timestamp = round(target_datetime.timestamp() * 1000)
    # print(timestamp)
    return timestamp
