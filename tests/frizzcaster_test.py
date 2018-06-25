import pytest
from app.frizzcaster import detect_ip, choose_location

# TODO: questions: api key, load other packages??

def test_detect_ip():
    print("testing ip...")
    assert detect_ip != None



def test_choose_location():
    print("testing location choice...")
    country = "United States"
    location_input = choose_location(location_input = "07747")
    outcome = choose_location(country)
    assert outcome == "2192103"
