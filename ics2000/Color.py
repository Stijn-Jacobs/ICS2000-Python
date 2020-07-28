from ics2000.Bytes import *


def rgb_constrained(inp) -> int:
    if inp < 0:
        return 0
    elif inp > 255:
        return 255
    else:
        return round(inp)


class rgb:
    def __init__(self, r, g, b):
        self.r = rgb_constrained(r)
        self.g = rgb_constrained(g)
        self.b = rgb_constrained(b)

    def to_xyz(self):
        lower = 0.04045
        div = 12.92

        f5 = 0.055
        f6 = 1.055
        f7 = 2.4

        f1 = self.r / 255
        if f1 < lower:
            f1 /= div
        else:
            f1 = pow((f1 + f5) / f6, f7)

        f2 = self.g / 255
        if f2 < lower:
            f2 /= div
        else:
            f2 = pow((f2 + f5) / f6, f7)

        f3 = self.b / 255
        if f3 < lower:
            f3 /= div
        else:
            f3 = pow((f3 + f5) / f6, f7)

        return Xyz(0.4124564 * f1 + 0.3575761 * f2 + 0.1804375 * f3,
                   0.2126729 * f1 + 0.7151522 * f2 + 0.0721750 * f3,
                   f1 * 0.0193339 + f2 * 0.1191920 + f3 * 0.9503041)

    def serialize(self):
        xyx = self.to_xyz()
        y2 = 1
        x = xyx.x / (xyx.x + y2 + xyx.z)
        y = 1 / (xyx.x + y2 + xyx.z)
        f1 = int(x * MAX_UINT_16)
        f2 = int(y * MAX_UINT_16)
        print("saving: " + str(f1) + " : " + str(f2))
        arr = bytearray(4)
        insertint16(arr, f1 * 100, 0)
        insertint16(arr, f2 * 100, 2)
        return byte_to_int4(arr[2], arr[3], arr[0], arr[1])

    def __str__(self):
        return str([self.r, self.g, self.b])


class Xyz:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_rgb(self) -> []:
        limit = 0.0031308
        f6 = 0.42
        f7 = 1.055
        f8 = 0.055
        mul = 12.92

        f1 = 3.2404542 * self.x + -1.5371385 * self.y + -0.4985314 * self.z
        f2 = -0.9692660 * self.x + 1.8760108 * self.y + 0.0415560 * self.z
        f3 = 0.0556434 * self.x + -0.2040259 + self.y * 1.0572252 * self.z
        if f1 > limit:
            f1 = pow(f1, f6) * f7 - f8
        else:
            f1 *= mul

        if f2 > limit:
            f2 = pow(f2, f6) * f7 - f8
        else:
            f2 *= mul

        if f3 > limit:
            f3 = pow(f3, f6) * f7 - f8
        else:
            f3 *= mul

        f9 = max(f1, max(f3, f2))
        f1 /= f9
        f2 /= f9
        f3 /= f9
        return rgb(rgb_constrained(f1 * 255), rgb_constrained(f2 * 255), rgb_constrained(f3 * 255))

    def __str__(self):
        return str([self.x, self.y, self.z])
