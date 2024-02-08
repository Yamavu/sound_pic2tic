from binascii import unhexlify
from ctypes import Structure, BigEndianStructure, LittleEndianStructure, Union
from ctypes import c_uint8, c_uint16, c_uint32, c_bool,c_uint,c_int,c_byte,c_ubyte
from ctypes import memmove, pointer, sizeof
from struct import calcsize,unpack,pack
from sys import byteorder
class Header(BigEndianStructure):
    _fields_ = [
        ('a', c_uint, 3),
        ('b', c_uint, 1),
        ('c', c_uint, 3),
        ('d', c_uint, 1),
    ]
class H2():
    def __init__(self,header=Header()):
        self.header = header
    def tohexstr(self) -> str:
        b = bytes(self.header)
        #b = int.from_bytes(b, byteorder=byteorder)
        return b#.rstrip(b'\x00').hex()
    @classmethod
    def fromhexstr(cls,hx):
        dataBytes=bytes.fromhex(hx)
        print(dataBytes)
        c=Header()
        memmove(pointer(c), dataBytes, sizeof(c))
        return c

h = Header(
    a=0b111,
    b=0b0,
    c=0b011,
    d=0b0,
)
h=Header()
h.a=7
h.b=False
h.c=3
h.d=False

d=0b11100110
b = bytes(h)
b = int.from_bytes(b, byteorder=byteorder)
hx = h.tohexstr()
print(hx,f"{d:02x}")
assert b == d
#assert hx == f"{d:02x}"
h2=H2.fromhexstr(hx)
print(h2.tohexstr(), h.tohexstr())