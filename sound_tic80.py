import math
from dataclasses import dataclass
import re
from typing import List

@dataclass
class Tic80sfxFlags:
    speaker_l:bool
    speaker_r:bool
    arp_down:bool
    pitchx16:bool
    loop_vol_start  :int
    loop_vol_size   :int
    loop_wav_start  :int
    loop_wav_size   :int
    loop_arp_start  :int
    loop_arp_size   :int
    loop_pitch_start:int
    loop_pitch_size :int
    @classmethod
    def from_str(cls,sfx_str):
        # 4020 00623900
        assert re.match(r"[\dA-F]{12}",sfx_str)
        spk = int(sfx_str[3],base=16)
        speaker_l=(spk % 2 == 0)
        speaker_r=(spk // 2 % 2 == 0)
        arp_down = (sfx_str[2] == "8")
        pitchx16 = (sfx_str[1] == "c")
        loop_wav_start = int(sfx_str[6])
        loop_wav_size = int(sfx_str[7])
        loop_vol_start = int(sfx_str[6])
        loop_vol_size = int(sfx_str[7])
        loop_arp_start = int(sfx_str[8])
        loop_arp_size = int(sfx_str[9])
        loop_pitch_start = int(sfx_str[10])
        loop_pitch_size = int(sfx_str[11])
        Tic80sfxFlags(speaker_l,speaker_r,arp_down,pitchx16,loop_vol_start,loop_vol_size,loop_wav_start,loop_wav_size,loop_arp_start,loop_arp_size,loop_pitch_start,loop_pitch_size)
    def str(self):
        sfx_str = ["0"] * 12
        spk = 0
        if not self.speaker_l:
            spk = spk + 1
        if not self.speaker_r:
            spk = spk + 2
        sfx_str[3] = str(spk)
        if self.arp_down:
            sfx_str[2] = "8"
        if self.pitchx16:
            sfx_str[1] = "c"
        for i,val in enumerate([
            self.loop_wav_start, self.loop_wav_size ,  \
            self.loop_vol_start,self.loop_vol_size ,   \
            self.loop_arp_start, self.loop_arp_size ,  \
            self.loop_pitch_start,self.loop_pitch_size \
            ]):
            sfx_str[6+i] = f"{val:01X}"
        
@dataclass
class Tic80sfx_pt:
    vol:float
    wave:int
    arp:float
    pitch:float

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


if __name__=="__main__":
    #for i in range(8):
    #    print(f"{i:03}:"+p8waves(i).get_wave())
    s="040004010402140314042405240634074408640074008400a400b400c400d400e400e400f400f400f400f400f400f400f400f400f400f400f400f400402000620000"
    sfx=Tic80sfx.from_str(s)
    print(sfx.debug())
