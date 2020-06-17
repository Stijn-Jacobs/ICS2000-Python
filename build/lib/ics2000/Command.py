import numpy as np
from .Cryptographer import *


class Command:

    def __init__(self):
        self._header = bytearray(43)
        self._data = bytearray()
        self.setframe(1)

    def setframe(self, num):
        if 0 <= num <= 255:
            self._header[0] = np.uint8(num)

    def settype(self, num):
        if 0 <= num <= 255:
            self._header[2] = np.uint8(num)

    def setmac(self, mac: str):
        arr = bytes.fromhex(mac.replace(":", ""))
        if len(arr) == 6:
            self.insertbytes(arr, 3)

    def setmagic(self):
        num = 653213
        self.insertint32(num, 9)

    def setentityid(self, entityid):
        self.insertint32(entityid, 29)

    def setdata(self, data, aes):
        self._data = encrypt(data, aes)

    def getcommand(self) -> str:
        self.insertint16(len(self._data), 41)
        return self._header.hex() + self._data.hex()

    def insertbytes(self, arr, start):
        for i in range(len(arr)):
            self._header[i + start] = arr[i]

    def insertint32(self, num, start):
        self._header[start] = np.uint8(num & 0xFF)
        self._header[start + 1] = np.uint8(num >> 8 & 0xFF)
        self._header[start + 2] = np.uint8(num >> 16 & 0xFF)
        self._header[start + 3] = np.uint8(num >> 24 & 0xFF)

    def insertint16(self, num, start):
        self._header[start] = np.uint8(num & 0xFF)
        self._header[start + 1] = np.uint8(num >> 8 & 0xFF)




