import pytest
#from pathlib import Path
#from argparse import Namespace
from sound_tic80 import Tic80sfx, Tic80sfx_pt,Tic80sfxFlags



@pytest.fixture
def sfx() -> str:
    _sfx =  "0400" + "0401" + "0402" + "1403" + "1404" + "2405" + "2406" + "3407" + "4408" + "6400" + \
            "7400" + "8400" + "a400" + "b400" + "c400" + "d400" + "e400" + "e400" + "f400" + "f400" + \
            "f400" + "f400" + "f400" + "f400" + "f400" + "f400" + "f400" + "f400" + "f400" + "f400" + \
            "4020" + "00" + "62" + "3f" + "0f"
    return _sfx

@pytest.fixture
def pattern() -> str:
    return "000000" + "500006" + "000000" + "000000" + "000000" + "c00006" + "000000" + "000000" + \
           "000000" + "000000" + "c00008" + "000000" + "000000" + "a00008" + "000000" + "000000" + \
           "900008" + "000000" + "000000" + "a00008" + "000000" + "000000" + "000000" + "000000" + \
           "500006" + "000000" + "000000" + "400006" + "000000" + "000000" + "000000" + "600006" + \
           "000000" + "000000" + "000000" + "c00006" + "000000" + "000000" + "900006" + "000000" + \
           "000000" + "b00006" + "000000" + "000000" + "d00006" + "000000" + "000000" + "b00006" + \
           "000000" + "000000" + "000000" + "900006" + "000000" + "000000" + "c00006" + "000000" + \
           "000000" + "b00006" + "000000" + "000000" + "000000" + "400006" + "000000" + "000000"
@pytest.fixture
def track():
    return "10fb30000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
@pytest.fixture
def wave_box() -> str:
    return "00000000ffffffff00000000ffffffff"
"""
def test_sfxflags_to_hex(sfx):
    _sfxflags = sfx[-13:-1]
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.to_hex_str() == _sfxflags
"""
def test_sfxflags(sfx):
    flags = Tic80sfxFlags(speed=4,octave=2)
    hexrepr = "100000000000"
    data=bytes.fromhex(flags.to_hex_str())
    print(f"{data[0]:08b}")
    hx = flags.to_hex_str()
    assert len(hx) == 12
    assert hx == hexrepr
def test_sfxflags_2():
    hex_str = "020312345678"
    print(hex_str)
    flags = Tic80sfxFlags.from_hex_str(hex_str)
    assert flags.speed == 4
    assert flags.reverse == False
    print(flags)
    print(flags.to_hex_str())
    assert hex_str == flags.to_hex_str()
def text_sfx(sfx):
    #s = "000000110022103310442055206630774088609070a080b0a0c0b0d0c0e0d0f0e000e000e000f000f000f000f000f000f000f000f000f000f000f000030012345678"
    _sfx = Tic80sfx.from_hex_str(sfx)
    assert len(_sfx.pts) == 30
    
    print(_sfx)

def text_sfx_pt():
    s = "f001"
    _sfx = Tic80sfx_pt.from_hex_str(s)
    assert _sfx.pitch == 1
    assert _sfx.volume == 0
    s_ = _sfx.to_hex_str()
    assert s == s_

"""def test_flags_sp4():
    _sfxflags = "304012345678"# spd: 4
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.speed == 4
def test_flags_sp0():
    _sfxflags = "df7012345678" #   spd:3
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.speed == 3
    assert flags.pitch16x is True
    assert flags.reverse is True

def test_flags_sp6():
    _sfxflags = "020312345678" #   spd:6
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    print(flags)
    assert flags.speed == 6
    assert flags.stereo_left is False
    assert flags.stereo_right is False
def test_flags_sp7():
    _sfxflags = "537012345678" #spd:7
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.speed == 7
def test_flags_sp4_x16():
    _sfxflags = "b04012345678" #  px16 - spd:4
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.speed == 4
    assert flags.pitch16x is True
    assert flags.reverse is False
"""
"""def test_flags_sp5():
    _sfxflags = "080012345678"
    flags = Tic80sfxFlags.from_hex_str(_sfxflags)
    assert flags.speed == 4
    assert flags.pitch16x is False
    assert flags.reverse is True
    assert flags.to_hex_str()[0:4] == _sfxflags[0:4]
def test_flags_new():
    hex_str="df7012345678"
    flags = Tic80sfxFlags.from_hex_str(hex_str)
    print(flags)
    assert hex_str == flags.to_hex_str()
"""