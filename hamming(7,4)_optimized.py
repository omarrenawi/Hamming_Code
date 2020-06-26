from typing import List, Generator


def encode(bits):
    """

    @parm bits: a string of 4 bits to be encoded
    @return: a string of 7 bits (encoding)
    """
    assert len(bits) == 4

    c3, c5, c6, c7 = int(bits[0]), int(bits[1]), int(bits[2]), int(bits[3])
    c1 = str((c3 + c5 + c7) % 2)
    c2 = str((c3 + c6 + c7) % 2)
    c4 = str((c5 + c6 + c7) % 2)
    
    return ("".join([c1, c2, str(c3), c4, str(c5), str(c6), str(c7)])).encode()


def decode(symbol):
    """
    
    @parm symbol: the symbol to be decoded
    @return: The decoded symbol (With error correction if necessary)
    """
    assert len(symbol) == 7

    c1, c2, c3, c4, c5, c6, c7 = symbol[0], symbol[1], symbol[2], symbol[3], symbol[4], symbol[5], symbol[6]
    s1 = (int(c1) + int(c3) + int(c5) + int(c7)) % 2
    s2 = (int(c2) + int(c3) + int(c6) + int(c7)) % 2
    s3 = (int(c4) + int(c5) + int(c6) + int(c7)) % 2
    
    byte = bytes([int(symbol, 2)])
    if s1 + s2 + s3:
        idx = s1 + s2 * 2 + s3 * 4
        byte = bytes([ord(byte) ^ (1 << (7 - idx))])


    b = bin(ord(byte))[2:].zfill(7)
    b = b[1:] if len(b) > 7 else b
    return  b[2] + b[4] + b[5] + b[6]



def mm_encode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:
    
    bytes_buffer = []
    to_be_sent = b""

    for byte in source:
       
        bytes_buffer.append(byte)

        
        if len(bytes_buffer) < 4:
            continue

        for byte_ in bytes_buffer:
            b = bin(ord(byte_))[2:].zfill(8)
            h = b[:4]
            l = b[4:]
            to_be_sent += encode(h)    
            to_be_sent += encode(l)

        for i in range(0, 56, 8):
            res = bytes([int(to_be_sent[i:i+8], 2)])
            yield res
    
        bytes_buffer = []
        to_be_sent = b""

    if bytes_buffer:
        for byte_ in bytes_buffer:
            b = bin(ord(byte_))[2:].zfill(8)
            h = b[:4]
            l = b[4:]

            for i in [h, l]:
                res = encode(i)
                res = bytes([int(res, 2)])
                yield res



def mm_decode(source: Generator[bytes, None, None]) -> Generator[bytes, None, None]:

    tmp = b''
    received_bits = ""
    received_symbols = ""

    for byte in source:

        b = bin(ord(byte))[2:].zfill(8)
        received_symbols += b

        if len(received_symbols) < 56:
            continue
        
        for i in range(0, len(received_symbols), 7):
            b = received_symbols[i:i+7]
            received_bits += decode(b)    
        
        received_symbols = ""
            
        if len(received_bits) == 32:
            for i in range(0, 32, 8):
                res = bytes([int(received_bits[i:i+8], 2)])
                yield res
            received_bits = ""
        else:
            continue
        
    if received_bits:
        for i in range(0, len(received_bits), 7):
            res = bytes([int(received_bits[i:i+7], 2)])
            yield res
            received_bits = ""
