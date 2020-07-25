from ics2000.Color import *
from ics2000.Bytes import *


def deserialize_yxy_to_rgb(f) -> []:
    arr = bytearray(4)
    insertint32(arr, f, 0)
    x = round(byte_to_int2(arr[2], arr[3]) / MAX_UINT_16, 4)
    y = round(byte_to_int2(arr[0], arr[1]) / MAX_UINT_16, 4)
    y2 = 1
    xyz = Xyz(round(y2 / y * x, 4), y2, round(y2 / y * (1 - x - y), 4))
    return xyz.to_rgb()
