import numpy as np

MAX_UINT_16 = pow(2.0, 16.0) - 1.0


def insertint32(arr, num, start):
    arr[start] = np.uint8(num & 0xFF)
    arr[start + 1] = np.uint8(num >> 8 & 0xFF)
    arr[start + 2] = np.uint8(num >> 16 & 0xFF)
    arr[start + 3] = np.uint8(num >> 24 & 0xFF)


def insertint16(arr, num, start):
    arr[start] = np.uint8(num & 0xFF)
    arr[start + 1] = np.uint8(num >> 8 & 0xFF)


def insertbytes(arr, inp, start):
    for i in range(len(inp)):
        arr[i + start] = inp[i]


def byte_to_int2(byte1, byte2) -> int:
    return (byte1 & 0xFF | (byte2 & 0xFF) << 8) & 0xFFFF


def byte_to_int4(byte1, byte2, byte3, byte4) -> int:
    return (byte1 & 0xFF | (byte2 & 0xFF) << 8 | (byte3 & 0xFF) << 16 | (
            byte4 & 0xFF) << 24) & 0xFFFF
