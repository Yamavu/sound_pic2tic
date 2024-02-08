import math
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import List
import bitstring

# https://github.com/nesbox/TIC-80/wiki/RAM

FLAGS_BITFORMAT = ", ".join(
    ["bool","uint:3"] * 2 +
    ["uint:4, bool, bool, uint:2"] +
    ["uint:4"] * 8 
)
SFX_PT_BITFORMAT = ", ".join(["uint:4"] * 4 )

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
    @classmethod
    def from_hex_str(cls, hex_str:str):
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
        f = cls( *s_ )
        return f
    def to_hex_str(self):
        s_ = list(asdict(self).values())
        s_[1] = s_[1]-1
        s_[3] = (s_[3]+4)%8 # 5,6,7,0,1,2,3,4 -> 0-7
        s_[4] = s_[4]
        s : bitstring.BitStream = bitstring.pack(FLAGS_BITFORMAT, *s_)
        return s.hex

@dataclass
class Tic80sfx_pt:
    volume:int # 0-15
    wave:int # 0-15
    arpeggio:int # 0-15
    pitch:int # -7 - 0 - 7

    @classmethod
    def from_hex_str(cls,hex_str):
        s= bitstring.Bits("0x"+hex_str)
        s_ = s.unpack(SFX_PT_BITFORMAT)
        pt = cls(
            volume=15-s_[0],
            wave=s_[1],
            arpeggio=s_[2],
            pitch=s_[3]
        )
        return pt
    def to_hex_str(self):
        s_ = list(asdict(self).values())
        s_[0] = 15-s_[0]
        s : bitstring.BitStream = bitstring.pack(SFX_PT_BITFORMAT, *s_)
        return s.hex


@dataclass
class Tic80sfx:
    pts:List[Tic80sfx_pt] # len(30)
    flags:Tic80sfxFlags

    @classmethod
    def from_hex_str(cls,sfx_str):
        pts=[]
        #assert re.match(r"[\da-f]{132}",sfx_str)
        for i in range(30):
            pt_str = sfx_str[4*i:4*i+4]
            pts.append(Tic80sfx_pt.from_hex_str(pt_str))
        #assert len(pts) == 30
        flags=Tic80sfxFlags.from_hex_str(sfx_str[-12:])
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

def read_file(path:Path):
    sfx_list = {}
    sfx_id = None
    for line in path.read_text().split("\n"):
        if line == "-- </SFX>":
            sfx_id = None
        elif sfx_id is not None:
            print(line)
            m = re.match(r"\-\-\s+([\da-f]{3})\:([\da-f]{132})",line)
            sfx_id = int(m.group(1))
            sfx_list[sfx_id] = Tic80sfx.from_hex_str(m.group(2))
        elif line == "-- <SFX>":
            sfx_id = 0
    return(sfx_list)

if __name__=="__main__":
    for sfx in read_file(Path(r"D:\mine\code\TIC-80\sound_pic2tic\waves.lua")).items():
        print(sfx)