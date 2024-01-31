

#010e00000764518000180001800000665000000000005635086451800018000180000166500000000000663507645180001800018000006650000000000056350864518000180001800001665000000000006635
import math
from pathlib import Path
import itertools
import binascii
import re

file=Path("./Cab Ride (v1.2).p8")

class p8note:
    def __init__(self,data:str) -> None:
        #from hexstring
        print(len(data))
        assert len(data)==5
        self.scale=int(data[0:1])
        self.waveform=int(data[2]) #0 sine, 1 triangle, 2 sawtooth, 3 long square, 4 short square, 5 ringing, 6 noise, 7 ringing sine; 8-F are the custom 
        self.volume=int(data[3])
        self.effect=int(data[4]) #0 none, 1 slide, 2 vibrato, 3 drop, 4 fade_in, 5 fade_out, 6 arp fast, 7 arp slow
    def debug(self)->str:
        w=["sine", "triangle", "sawtooth", "long square", "short square", "ringing", "noise", "ringing sine"]
        w+= [f"custom{i}" for i in range(8)]
        e=[ "none", "slide", "vibrato", "drop", "fade_in", "fade_out", "arp fast", "arp slow"]
        s=f"scale: {self.scale}\n"
        s+=f"waveform: {w[self.waveform]}\n"
        s+=f"volume: {self.volume}\n"
        s+=f"effect: {e[self.effect]}"
        return s
class p8waves:
    def __init__(self,waveform) -> None:
        self.waveform=waveform
    def get_wave(self):
        s=""
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
            pass # custom
        wave=[int(fun(x)) for x in range(l)]
        s="".join([f'{x:01X}' for x in wave])
class p8sfx:
    def __init__(self,data:str):
        self.b=b=bytearray(binascii.unhexlify(data))
        assert len(b)==84
        self.mode_filter = b[0]
        self.dur = int(b[1]) # in multiples of 1/128 second
        self.loop_start = int(b[2])
        self.loop_end = int(b[3])
        self.notes=[p8note(data[i:i+5]) for i in range(4,84,5)]
        print([i for i in range(4,84,5)])
    def __str__(self) -> str:
        return self.b.hex()
    def debug(self) -> str:
        s="p8 sound\n"
        s+=f"dur: {self.dur}\n"
        s+=f"loop: {self.loop_start}-{self.loop_end}\n"
        return s
def encode_booleans(bool_lst):
    res = 0
    for i, bval in enumerate(bool_lst):
        res += int(bval) << i
    return res

def decode_booleans(intval, bits):
    res = []
    for bit in range(bits):
        mask = 1 << bit
        res.append((intval & mask) == mask)
    return res

class p8music:
    def __init__(self,data:str) -> None:
        data = list(data.split(" "))
        assert len(data)==2
        assert len(data[0])==2
        assert len(data[1])==8
        #print(repr(data[1]))
        b1 = bytearray.fromhex(data[0])
        b2 = bytearray.fromhex(data[1])
        self.flags=decode_booleans(int.from_bytes(b1),8)
        self.sfxids=[None,None,None,None]
        for i in range(4):
            if b2[i]>=64:
                self.sfxids[i]=b2[i]-64
                self.sfxids_active = False
                self.sfxids_channel = b2[i]>>6
            else:
                self.sfxids[i]=b2[i]
                self.sfxids_active = True
                self.sfxids_channel = b2[i]>>6
    def debug(self) -> str:
        flags=["begin pattern loop","end pattern loop","stop at end of pattern"]
        s = f"flags: \n"
        for i,flag in enumerate(flags):
            s += f"\t{flag}:\t{self.flags[i]}\n"
        s += "sfx: \n"
        for i,sfxid in enumerate(self.sfxids):
            s+=f"\tChannel {sfxid>>6}: "
            if sfxid>=64: 
                s += f"{sfxid-64}"+" (silent)\n" 
            else:
                s += f"{sfxid}\n"
        return s

# datatype sfx,music

class p8file:
    def __init__(self,p8file:Path) -> None:
        self.music = []
        self.sfx = []
        with open(p8file,"r",encoding="utf-8",errors="ignore") as f:
            lines = f.readlines()
            for i,line in enumerate(lines):
                if line == "__sfx__\n":
                    n=i+1
                    while re.match(r"[\da-f]{168}\n",lines[n]):
                        self.sfx.append(p8sfx(lines[i+1].rstrip("\n")))
                        n = n + 1
                if line == "__music__\n":
                    n=i+1
                    while re.match(r"[\d]{2} [\da-f]{8}\n",lines[n]):
                        self.music.append(p8music(lines[i+1].rstrip("\n")))
                        n = n + 1
    def debug(self):
        return f"p8file with {len(self.music)} music tracks using {len(self.sfx)} sounds"
d=p8file(file)
print(d.debug())