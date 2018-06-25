import pytest
from app.frizzcaster import detect_ip, frizz_adviser_now, frizz_adviser_daily



def test_detect_ip():
    print("testing ip...")
    assert detect_ip != None

def test_frizz_adviser_now():
    dew_point = 30
    precipitation = 0
    wind_speed = 5

    assert frizz_adviser_now(dew_point, precipitation, wind_speed) == ('low', 'LOW DEWPOINT', 'LITTLE TO NO PRECIPITATION', 'CALM WINDS')

def test_frizz_adviser_daily():
    frizz_score = 4
    assert frizz_adviser_daily(frizz_score) == "high"
