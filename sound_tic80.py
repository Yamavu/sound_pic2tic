import math
from dataclasses import dataclass, asdict
import re
from ctypes import memmove, pointer, sizeof
from ctypes import c_int8,c_uint8, BigEndianStructure,LittleEndianStructure,Structure
from typing import List
import bitstring

# https://github.com/nesbox/TIC-80/wiki/RAM

FLAGS_BITFORMAT = ", ".join(
    ["bool","uint:3"] * 2 +
    ["uint:4, bool, bool, uint:2"] +
    ["uint:4"] * 8 
)

class Flags_bits(LittleEndianStructure):
    _fields_ = [
        ("pitch16x", c_uint8, 1),
        ("octave", c_uint8, 3),
        ("reverse", c_uint8, 1),
        ("speed", c_uint8, 3),
        ("note", c_uint8, 4),
        ("stereo_left", c_uint8, 1),
        ("stereo_right", c_uint8, 1),
        ("temp", c_uint8, 2),
        ("loop_vol_start", c_uint8, 4),
        ("loop_vol_size", c_uint8, 4),
        ("loop_wav_start", c_uint8, 4),
        ("loop_wav_size", c_uint8, 4),
        ("loop_arp_start", c_uint8, 4),
        ("loop_arp_size", c_uint8, 4),
        ("loop_pitch_start", c_uint8, 4),
        ("loop_pitch_size", c_uint8, 4),
    ]
@dataclass
class Tic80sfxFlags:
    """ | .---------------------.  |
        | | octave       | 3bit |  |
        | | pitch16x     | 1bit |  |
        | | speed        | 3bit |  |
        | | reverse      | 1bit |  |
        | | note         | 4bit |  |
        | | stereo_left  | 1bit |  |
        | | stereo_right | 1bit |  |
        | | temp         | 2bit |  |
        | '---------------------'  |"""
    pitch16x        :bool = False
    octave          :int = 0        # last note played
    reverse         :bool = False   # arpeggio down
    speed           :int = 4
    note            :int = 0
    stereo_left     :bool = True
    stereo_right    :bool = True
    temp            :int = 0
    loop_vol_start  :int = 0
    loop_vol_size   :int = 0
    loop_wav_start  :int = 0
    loop_wav_size   :int = 0
    loop_arp_start  :int = 0
    loop_arp_size   :int = 0
    loop_pitch_start:int = 0
    loop_pitch_size :int = 0
    
    def to_hex_str(self) -> str:
        dataStruct = Flags_bits(
            pitch16x = not bool(self.pitch16x),
            octave = (self.octave+4)%8,
            reverse = not bool(self.reverse),
            speed = (self.speed+4)%8,
            note = self.note,
            stereo_left = not(self.stereo_left),
            stereo_right = not(self.stereo_right),
            temp = self.temp,
            loop_vol_start = self.loop_vol_start,
            loop_vol_size = self.loop_vol_size,
            loop_wav_start = self.loop_wav_start,
            loop_wav_size = self.loop_wav_size,
            loop_arp_start = self.loop_arp_start,
            loop_arp_size = self.loop_arp_size,
            loop_pitch_start = self.loop_pitch_start,
            loop_pitch_size = self.loop_pitch_size,
        )
        b = bytes(dataStruct)
        return b.hex()
    @classmethod
    def from_hex_str(cls,hex_str):
        data=bytes.fromhex(hex_str)
        struct_=Flags_bits()
        memmove(pointer(struct_), data, sizeof(struct_))
        #print("struct_.speed", struct_.speed)
        return cls(
            pitch16x = bool(struct_.pitch16x),
            octave = (int(struct_.octave)-6)%8,
            speed = (int(struct_.speed)-4)%8,
            reverse = not bool(struct_.reverse),
            note = int(struct_.note),
            stereo_left = not bool(struct_.stereo_left),
            stereo_right = not bool(struct_.stereo_right),
            loop_vol_start = int(struct_.loop_vol_start),
            loop_vol_size = int(struct_.loop_vol_size),
            loop_wav_start = int(struct_.loop_wav_start),
            loop_wav_size = int(struct_.loop_wav_size),
            loop_arp_start = int(struct_.loop_arp_start),
            loop_arp_size = int(struct_.loop_arp_size),
            loop_pitch_start = int(struct_.loop_pitch_start),
            loop_pitch_size = int(struct_.loop_pitch_size),
            temp = int(struct_.temp),
        )

    @classmethod
    def _from_str(cls,sfx_str):
        assert len(sfx_str) == 12
        assert re.match(r"[\dA-Fa-f]{12}",sfx_str)
        hex = bytearray.fromhex(sfx_str)
        spk = int(sfx_str[3],base=16)
        speaker_l=(spk % 2 == 0)
        speaker_r=(spk // 2 % 2 == 0)
        arp_down = (int(sfx_str[1],16) > 7)
        pitchx16 = (int(sfx_str[0],16) > 7)
        speed = (int(sfx_str[1],16)-4)%8
        loop_wav_start = int(sfx_str[4],16)
        loop_wav_size = int(sfx_str[5],16)
        loop_vol_start = int(sfx_str[6],16)
        loop_vol_size = int(sfx_str[7],16)
        loop_arp_start = int(sfx_str[8],16)
        loop_arp_size = int(sfx_str[9],16)
        loop_pitch_start = int(sfx_str[10],16)
        loop_pitch_size = int(sfx_str[11],16)
        return Tic80sfxFlags(speaker_l,speaker_r,arp_down,pitchx16,speed,loop_vol_start,loop_vol_size,loop_wav_start,loop_wav_size,loop_arp_start,loop_arp_size,loop_pitch_start,loop_pitch_size)
    def _to_hex(self):
        sfx_str = ["0"] * 12
        # sfx_str[0]=?
        sfx_str[1] = f"{(self.speed+4)%8:1x}"
        if self.pitch16x:
            sfx_str[0] = f"{int(sfx_str[0],16)+8:1x}"
        if self.reverse:
            sfx_str[1] = f"{int(sfx_str[1],16)+8:1x}"
        spk = 0
        spk = spk + 1 if not self.stereo_left else spk
        spk = spk + 2 if not self.stereo_right else spk
        sfx_str[3] = str(spk)
        for i,val in enumerate([
            self.loop_wav_start, self.loop_wav_size ,  \
            self.loop_vol_start,self.loop_vol_size ,   \
            self.loop_arp_start, self.loop_arp_size ,  \
            self.loop_pitch_start,self.loop_pitch_size \
            ]):
            sfx_str[4+i] = f"{val:1x}"
        return "".join(sfx_str)
    def diff(self,other):
        o = asdict(other)
        res = {}
        difference = False
        for k,v in asdict(self).items():
            if k in o and not o[k] == v:
                difference = True
                res [k] = (v,o[k])
                print(f"{k}\t{res [k]}")
        return res

@dataclass
class Tic80sfx_pt:
    vol:float # 0-1
    wave:int
    arp:float # 0-1
    pitch:float # 0-1

@dataclass
class Tic80sfx:
    pts:List[Tic80sfx_pt]
    flags:Tic80sfxFlags
        
    def debug(self):
        s=""
        s+="vol:"+" ".join([f"{pt.vol:02.2f}" for pt in self.pts])+"\n"
        s+="wave:"+" ".join([f"{pt.wave:d}" for pt in self.pts])+"\n"
        s+="arp:"+" ".join([f"{pt.arp:02.2f}" for pt in self.pts])+"\n"
        s+="pitch:"+" ".join([f"{pt.pitch:02.2f}" for pt in self.pts])+"\n"
        return s
    @classmethod
    def from_str(cls,sfx_str):
        # 040004000400140014002400240034004400640074008400a400b400c400d400e400e400f400f400f400f400f400f400f400f400f400f400f400f400205000000000
        # 04 00 04 00 04 00 14 00 14 00 24 00 24 00 34 00 44 00 64 00 74 00 84 00 a4 00 b4 00 c4 00d400e400e400f400f400f400f400f400f400f400f400f400f400f400f400205000000000
        # 0 - 4 - 0
        # volume 0-F , wave 0-f arpeg 0-F, pitch 0-F
        # 0 : 100% - F: 0%, , 0: 0 1-7: + 8-F -
        # wave - volume - chord - pitch
        # flags: 205000000000
        pts=[]        
        for i in range(30):
            vol=1-int(sfx_str[4*i+0],16)/15
            wave=int(sfx_str[4*i+1],16)
            arp=int(sfx_str[4*i+2],16)/15
            p=int(sfx_str[4*i+3],16)
            p=p if p<8 else -15+p
            pitch = p / 7
            pts.append(Tic80sfx_pt(vol,wave,arp,pitch))
        flags=Tic80sfxFlags(True,True,False,False,0,0,0,0,0,0,0,0)
        return cls(pts,flags)

class p8waves:
    def __init__(self,waveform) -> None:
        self.waveform=waveform
    def get_wave(self):
        l=32
        if self.waveform==0:
            fun=lambda i : (math.sin(i*math.pi/(0.5*l))/2+0.5)*15
        elif self.waveform==1:
            fun=lambda i: i if i < 16 else 31-i
        elif self.waveform==2:
            fun=lambda i : i%16
        elif self.waveform==3:
            fun=lambda i: 15 if i < 16 else 0
        elif self.waveform==4:
            fun=lambda i: 15 if i%16 < 8 else 0
        elif self.waveform==5:
            fun=lambda i : (math.sin(i%16*math.pi/(0.5*l))/2+0.5)*7
        elif self.waveform==6:
            fun=lambda i : 0
        elif self.waveform==7:
            fun=lambda i : math.sin(i%16*math.pi/8)*7+8 if i < 16 else math.sin(i%16*math.pi/8)*4+8
        else:
            pass #custom
        wave=[int(fun(x)) for x in range(l)]
        return "".join([f'{x:01X}' for x in wave])


        """| .----------ctave       | 3bit |  |
        | | -----------.  |
        | | opitch16x     | 1bit |  |
        | | speed        | 3bit |  |
        | | reverse      | 1bit |  |
        | | note         | 4bit |  |
        | | stereo_left  | 1bit |  |
        | | stereo_right | 1bit |  |
        | | temp         | 2bit |  |
        | '---------------------'  |"""

def from_hex_str(hex_str:str):
    # assert isinstance(hex_str, str)
    s= bitstring.Bits("0x"+hex_str)
    s_ = s.unpack(FLAGS_BITFORMAT)
    # octave 0-7 -> 1-8
    s_[1] = s_[1]+1 if s_[4] < 12 else s_[1]+2 
     # 5,6,7,0,1,2,3,4 -> 0-7
    s_[3] = (s_[3]-4)%8
    # Note numbers 0...11 are mapped to C...B.
    # Note numbers 12...15 are mapped to C...D# on the next higher octave,
    # which is an "unintended" SFX feature.
    s_[4] = s_[4] if s_[4] < 12 else s_[4]-12 
    f = Tic80sfxFlags( *s_ )
    return f
def to_hex_str(flags:Tic80sfxFlags):
    s_ = list(asdict(flags).values())
    s_[1] = s_[1]-1
    s_[3] = (s_[3]+4)%8 # 5,6,7,0,1,2,3,4 -> 0-7
    s_[4] = s_[4]
    s : bitstring.BitStream = bitstring.pack(FLAGS_BITFORMAT, *s_)
    return s.hex

hex_str = "020312345678"
print(hex_str)
flags = from_hex_str(hex_str)
print(flags)
print(to_hex_str(flags))
assert hex_str == to_hex_str(flags)

if __name__=="__main__":
    #for i in range(8):
    #    print(f"{i:03}:"+p8waves(i).get_wave())
    
    #s="040004010402140314042405240634074408640074008400a400b400c400d400e400e400f400f400f400f400f400f400f400f400f400f400f400f400402000620000"
    #sfx=Tic80sfx.from_str(s)
    #print(sfx.debug())
    pass