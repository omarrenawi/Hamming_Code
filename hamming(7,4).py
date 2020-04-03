from typing import List, Generator


def mm_encode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    for byte in source:
        b = bin(ord(byte))[2:].zfill(8)
        h = b[:4]
        l = b[4:]

        for i in [h, l]:
            c3, c5, c6, c7 = int(i[0]), int(i[1]), int(i[2]), int(i[3])
            c1 = str((c3 + c5 + c7) % 2)
            c2 = str((c3 + c6 + c7) % 2)
            c4 = str((c5 + c6 + c7) % 2)
            res = "".join([c1, c2, str(c3), c4, str(c5), str(c6), str(c7)])
            res = bytes([int(res, 2)])
            yield res


def mm_decode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:

    tmp = b''

    for byte in source:
        b = bin(ord(byte))[2:].zfill(7) if len(bin(ord(byte))) < 10 else bin(ord(byte))[3:]

        c1, c2, c3, c4, c5, c6, c7 = b[0], b[1], b[2], b[3], b[4], b[5], b[6]

        s1 = (int(c1) + int(c3) + int(c5) + int(c7)) % 2
        s2 = (int(c2) + int(c3) + int(c6) + int(c7)) % 2
        s3 = (int(c4) + int(c5) + int(c6) + int(c7)) % 2

        if s1 + s2 + s3:
            idx = s1 + s2 * 2 + s3 * 4
            byte = bytes([ord(byte) ^ (1 << (7 - idx))])

        b = bin(ord(byte))[2:].zfill(7)
        b = b[1:] if len(b) > 7 else b
        init_byte = b[2] + b[4] + b[5] + b[6]

        if tmp:
            tmp += init_byte
            byte = bytes([int(tmp, 2)])
            tmp = b''
            yield byte

        else:
            tmp = init_byte
