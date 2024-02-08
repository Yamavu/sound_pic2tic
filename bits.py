from ctypes import memmove, pointer, sizeof
from ctypes import c_uint8, BigEndianStructure

class Flags_bits(BigEndianStructure):
    _fields_ = [
        ("octave", c_uint8, 3),
        ("pitch16x", c_uint8, 1),
        ("speed", c_uint8, 3),
        ("reverse", c_uint8, 1),
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
from dataclasses import dataclass
@dataclass
class Tic80sfxFlags():
    octave          :int = 0
    pitch16x        :bool = False
    speed           :int = 4
    reverse         :bool = False # arpeggio down
    note            :int = 0
    stereo_left     :bool = True
    stereo_right    :bool = True
    loop_vol_start  :int = 0
    loop_vol_size   :int = 0
    loop_wav_start  :int = 0
    loop_wav_size   :int = 0
    loop_arp_start  :int = 0
    loop_arp_size   :int = 0
    loop_pitch_start:int = 0
    loop_pitch_size :int = 0
    temp            :int = 0
    
    def tohexstr(self) -> str:
        dataStruct = Flags_bits(
            octave = self.octave,
            pitch16x = self.pitch16x,
            speed = self.speed,
            reverse = self.reverse,
            note = self.note,
            stereo_left = self.stereo_left,
            stereo_right = self.stereo_right,
            loop_vol_start = self.loop_vol_start,
            loop_vol_size = self.loop_vol_size,
            loop_wav_start = self.loop_wav_start,
            loop_wav_size = self.loop_wav_size,
            loop_arp_start = self.loop_arp_start,
            loop_arp_size = self.loop_arp_size,
            loop_pitch_start = self.loop_pitch_start,
            loop_pitch_size = self.loop_pitch_size,
            temp = self.temp,
        )
        b = bytes(dataStruct)
        return b.hex()
    @classmethod
    def fromhexstr(cls,hex_str):
        data=bytes.fromhex(hex_str)
        struct_=Flags_bits()
        memmove(pointer(struct_), data, sizeof(struct_))
        return cls(
            octave = int(struct_.octave),
            pitch16x = int(struct_.pitch16x),
            speed = int(struct_.speed),
            reverse = bool(struct_.reverse),
            note = int(struct_.note),
            stereo_left = bool(struct_.stereo_left),
            stereo_right = bool(struct_.stereo_right),
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

