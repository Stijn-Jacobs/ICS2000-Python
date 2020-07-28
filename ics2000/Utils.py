from ics2000.Color import *
from ics2000.Bytes import *


def deserialize_yxy_to_rgb(f) -> []:
    arr = bytearray(4)
    insertint32(arr, f, 0)
    x = byte_to_int2(arr[2], arr[3]) / MAX_UINT_16
    y = byte_to_int2(arr[0], arr[1]) / MAX_UINT_16
    print("received: " + str(byte_to_int2(arr[2], arr[3])) + " : " + str(byte_to_int2(arr[0], arr[1])))
    print("received: " + str(x) + " : " + str(y))

    y2 = 1
    xyz = Xyz(((x * y2) / y), y2, ((1.0 - x - y) * (y2 / y)))

    print("starting xyz: " + str(xyz))
    return xyz.to_rgb()
