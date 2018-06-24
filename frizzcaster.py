#import csv
from dotenv import load_dotenv
import json
import os
import requests
import pytest
import pdb
from datetime import datetime
from dateutil.parser import parse

# TODO: which ones to load / directions?

# load environment variable
# TODO: how to share w/ prof?
load_dotenv()
api_key = os.environ.get("ACCUWEATHER_API_KEY") or "OOPS. Please set an environment variable named 'ACCUWEATHER_API_KEY'."

# check for 200 response (ok); otherwise, error connecting!
# turn json into dict
# then check if result is a list
# if yes, return; if no, add to list and then return
def parse_response(response):

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
    # when not 200 response status
        return "Error: " + str(e)

    if isinstance(response.text, str): # if not yet converted, then:
        response_text = json.loads(response.text)  # convert string to dictionary

    if isinstance(response_text, list):
        return response_text
    else:
        list_container = []
        list_container.append(response_text)
        return list_container



# detect a user's public ip address
# returns user's ip address as string
def detect_ip():
    ip_request_url = "http://myip.dnsomatic.com"
    ip_response = requests.get(ip_request_url)
    ip = ip_response.text
    return ip
    # TODO: add validation testing here?
    # TODO: like, if NONE or not in expected format, skip to check location input def

# uses a user's ip address to automatically geolocate them
# returns accuweather location key if user agrees the location is accurate
# else sends user to choose_location function to manually define location (with country as parameter for greater accuracy)
def location_key_by_ip():
    ip = detect_ip()
    request_url = f"http://dataservice.accuweather.com/locations/v1/cities/ipaddress?apikey={api_key}&q={ip}"
    response = requests.get(request_url)
    # print(response)
    location = parse_response(response=response)

    city = location[0]["EnglishName"]
    state = location[0]["AdministrativeArea"]["EnglishName"]
    country = location[0]["Country"]["EnglishName"]
    zip_code = location[0]["PrimaryPostalCode"]
    location_key = location[0]["Key"]

    while True:
        print("Do you want the Frizzcast for:")
        print(f"+ {city}, {state}  {zip_code} {country}? +".upper())
        print("-----")
        print("\n[Y] for YES")
        print("[N] for NO\n")
        user_decision = input("Enter your response: ").upper()

        if user_decision == "Y" or user_decision == "YES":
            return location_key
        elif user_decision == "N" or user_decision == "NO":
            print("\nGot it! You want a frizzcast for a different location.")
            return choose_location(country=country)
        else:
            print("\nOops! Your entry was invalid. Let's try again.\n")

# invites user to input location (as city + state and/or zip)
# will use the first entry in returned results of locations (either with same country as was geolocated or not if difference is detected)
# validation: list (locations) must have at least one item // otherwise, user is asked to try again
# returns accuweather location key if user agrees the location is accurate
# else user is invited to try again
def choose_location(country):
    global location_name
    ask_location = True
    ask_decision = True

    while ask_location:

        location_input = input("Enter a city and state OR zip code: ".upper())
        # location_input = "brooklyn new york"

        # TODO validate before making the call?

        request_url = f"http://dataservice.accuweather.com/locations/v1/search?apikey={api_key}&q={location_input}&offset=5"
        response = requests.get(request_url)
        locations = parse_response(response=response)


        if len(locations) >= 1:

            for location in locations:
                if country == location["Country"]["EnglishName"]:
                    locations = location
                    break
            # in case user is accessing app from a different country from desired frizzcast location
            if isinstance(locations, list):
                locations = locations[0]

            city = locations["EnglishName"]
            state = locations["AdministrativeArea"]["EnglishName"]
            country = locations["Country"]["EnglishName"]
            zip_code = locations["PrimaryPostalCode"]
                        # location_key is required to get local weather
            location_key = locations["Key"]



            ask_decision = True

            while ask_decision:


                print(f"\nYou selected:")
                print(f"+ {city}, {state}  {zip_code} {country} +".upper())
                print("-----")
                print("\nIs that correct?")
                print("[Y] for Yes")
                print("[N] for NO\n")
                user_decision = input("Enter your response: ").upper()

                if user_decision == "Y" or user_decision == "YES":
                    location_name = f"{city}, {state}  {zip_code} {country}".upper()
                    return location_key

                elif user_decision == "N" or user_decision == "NO":
                    print("\nOkay, let's try again.\n")
                    ask_decision = False
                    ask_location = True


                else:
                    print("\nDecision entry not valid. Let's try again.\n")
                    ask_location = False
                    ask_decision = True


        else:
            print("\nDarn! Your location entry was not valid. Please try again.\n")

# input from choose_location function --> location_key
# user asked to choose forecast type and brought to the related function to grab forecast results
def forecast_range(location_key):

    # TODO: future: get 120 hour forecast for better predictions (this is premium for most weather apis...)

    while True:
        print("\n+ Select a frizzcast from below +".upper())
        print("-----")
        print("[A] Right Now")
        print("[B] Today")
        print("[C] Five-Day Forecast")

        user_decision = input("\nEnter the letter indicating your choice: ").upper()

        if user_decision == "A":
            return frizzcast_current(location_key)
        elif user_decision in ("B", "C"):
            return frizzcast_five(location_key, forecast_date = user_decision)
        else:
            print("Your selection was invalid. Let's try that again.")

# input from forecast_range(): location_key
# raw weather data is collected from most current conditions
# two functions interpret (1) the conditions into an advisory (2) the date and time into reader-friendly text
# output is a dictionary with the results
def frizzcast_current(location_key):
        request_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={api_key}&details=true"
        response = requests.get(request_url)

        current_forecast = parse_response(response=response)

        if len(current_forecast) >= 1:

            observation_date_time = current_forecast[0]["LocalObservationDateTime"]

            # TODO: TRIM THE INFO YOU TAKE IN; SAME FOR INITIAL LOCATION CALL? THERE IS THAT LAG UP TOP
            dew_point_imperial = current_forecast[0]["DewPoint"]["Imperial"]["Value"]
            # dew_point_imperial_unit = current_forecast[0]["DewPoint"]["Imperial"]["Unit"]
            # dew_point_metric = current_forecast[0]["DewPoint"]["Metric"]["Value"]
            # dew_point_metric_unit = current_forecast[0]["DewPoint"]["Metric"]["Unit"]

            # humidity = current_forecast[0]["RelativeHumidity"]
            # humidity_unit = "%"

            # temperature_imperial = current_forecast[0]["Temperature"]["Imperial"]["Value"]
            # temperature_imperial_unit = current_forecast[0]["Temperature"]["Imperial"]["Unit"]
            # temperature_metric = current_forecast[0]["Temperature"]["Metric"]["Value"]
            # temperature_metric_unit = current_forecast[0]["Temperature"]["Metric"]["Unit"]

            precipitation_imperial = current_forecast[0]["Precip1hr"]["Imperial"]["Value"]
            # precipitation_imperial_unit = current_forecast[0]["Precip1hr"]["Imperial"]["Unit"]
            # precipitation_metric = current_forecast[0]["Precip1hr"]["Metric"]["Value"]
            # precipitation_metric_unit = current_forecast[0]["Precip1hr"]["Metric"]["Unit"]

            wind_speed_imperial = current_forecast[0]["Wind"]["Speed"]["Imperial"]["Value"]
            # wind_speed_imperial_unit = current_forecast[0]["Wind"]["Speed"]["Imperial"]["Unit"]
            # wind_speed_metric = current_forecast[0]["Wind"]["Speed"]["Metric"]["Value"]
            # wind_speed_metric_unit = current_forecast[0]["Wind"]["Speed"]["Metric"]["Unit"]

            # TODO: else error

            # accu_hair_frizz = na


        frizz_score = frizz_adviser_now(dew_point_imperial, precipitation_imperial, wind_speed_imperial)
        frizz_score = list(frizz_score)

        day_date_plus_time = time_readability(observation_date_time)

        results = {
        day_date_plus_time: frizz_score
        }

        return results

# TODO: continue describing functions
def frizzcast_five(location_key, forecast_date):
    request_url = f"http://dataservice.accuweather.com//indices/v1/daily/5day/{location_key}/42?apikey={api_key}&details=true"
    response = requests.get(request_url)

    daily_forecast = parse_response(response=response)

    # TODO: loop thru? now will show data for eitehr today or five days' woth
    if len(daily_forecast) >= 1:

        today_forecast = daily_forecast.pop(0)
        five_day_forecast = daily_forecast

        if forecast_date == "B":
            # today only
            frizz_score = today_forecast["CategoryValue"]
            frizz_score = frizz_adviser_daily(frizz_score)

            day_date = today_forecast["LocalDateTime"]
            day_date = date_readability(day_date)

            result = {
            day_date: frizz_score
            }


        elif forecast_date == "C":
            # five days' worth
            frizz_score = []
            day_date = []
            for day in five_day_forecast:
                single_frizz_score = day["CategoryValue"]
                advisory = frizz_adviser_daily(single_frizz_score)
                frizz_score.append(advisory)

                single_day_date = day["LocalDateTime"]
                single_day_date = date_readability(single_day_date)
                day_date.append(single_day_date)

                result = dict(zip(day_date, frizz_score))

        return(result)


            #TODO: quit program with this error?
    else:
        print("Unexpected error.")


def date_readability(day_date):
    day_date = parse(day_date)
    return day_date.strftime("%A %B %d, %Y")


def time_readability(day_date_plus_time):
    day_date_plus_time = parse(day_date_plus_time)
    return day_date_plus_time.strftime("%A %B %d, %Y at %I:%M:%S %p")
#
# # TODO: TRIM THE INFO YOU TAKE IN; SAME FOR INITIAL LOCATION CALL? THERE IS THAT LAG UP TOP


def frizz_adviser_now(dew_point, precipitation, wind_speed):
    # DEWPOINT SCALE - SYNTHESIZED INFO FROM VARIOUS HAIR BLOGS

    if dew_point < 50:
        dew_point_scale = 1
    elif dew_point >= 50 and dew_point < 55:
        dew_point_scale = 2
    elif dew_point >= 55 and dew_point < 60:
        dew_point_scale = 3
    elif dew_point >= 60 and dew_point < 70:
        dew_point_scale = 4
    else:
        # over 70
        dew_point_scale = 5

    # PRECIPITATION SCALE
    if precipitation <= 0:
        precipitation_scale = 1
    elif precipitation > 0 and precipitation < .098:
        precipitation_scale = 2
    elif precipitation >= .098 and precipitation < .3:
        precipitation_scale = 3
    elif precipitation >= .03 and precipitation < 2:
        precipitation_scale = 4
    else:
        # over 4
        precipitation_scale = 5

    # WIND SPEED SCALE - BEAUFORT SCALE
    if wind_speed < 6:
        wind_speed_scale = 1
    elif wind_speed >= 6 and wind_speed < 12:
        wind_speed_scale = 2
    elif wind_speed >= 12 and wind_speed < 19:
        wind_speed_scale = 3
    elif wind_speed >= 19 and wind_speed < 24:
        wind_speed_scale = 4
    else:
        # over 24
        wind_speed_scale = 5

    high = "high"
    medium = "medium"
    low = "low"

    why_precipitation = "PRECIPITATION"
    why_wind = "UNUSUALLY STRONG WINDS"
    why_high_dewpoint = "HIGH DEWPOINT"
    why_medium_dewpoint = "MEDIUM DEWPOINT"
    why_low_dewpoint = "LOW DEWPOINT"


    if precipitation_scale > 1 and dew_point_scale in (4, 5):
        return(high, why_precipitation, why_high_dewpoint)
    elif wind_speed_scale == 5 and dew_point_scale in (4, 5):
        return(high, why_wind, why_high_dewpoint)
    elif precipitation_scale > 1:
        return(high, why_precipitation)
    elif wind_speed_scale == 5:
        return(high, why_wind)
    elif dew_point_scale in (4, 5):
        return(high, why_high_dewpoint)
    elif dew_point_scale == 4 or dew_point_scale == 3:
        return(medium, why_medium_dewpoint)
    else:
        # dew point is scale 1; very low
        return(low, why_low_dewpoint)

def frizz_adviser_daily(frizz_score):
    high = "high"
    medium = "medium"
    low = "low"



    # TODO: create another def for the advisories?
    if frizz_score <= 1:
        return(low)
    elif frizz_score > 1 and frizz_score < 4:
        return(medium)
    else:
        # is 4 or 5
        return(high)


# the location key is KEY! jk but it's important - it tells us where the user is!
#     location_key = response_text[0]["Key"]



# TODO: FEED LOCATION INTO API (VIA ACCUWEATHER API) IN SOME SORT OF ACCEPTABLE WAY
# TODO: DO SOME RESEARCH ON HOW THEY ACCEPT LOCATIONS...TURN THEN INTO LONG+LAT?

# TODO: EXPLORE CURRENT FORECAST JSON --> FORM PARSING STRATEGY
# TODO: EXPLORE INDICES? FRIZZ CAST VS DEW POINT ETC

# TODO: TURN JSON INTO DICT

# TODO: GRAB THE FOLLOWING: DEW POINT, HAIR FRIZZ, HUMIDITY, TEMERATURE, WIND GUSTS, PRECIPITATION
# TODO: STORE AS VARIABLES



# TODO: DETERMINE DIFFERING LEVELS OF FRIZZ CULPRITS (EX: LOW-->HIGH DEW POINT)
# TODO: CREATE YOUR OWN EQUATION
# TODO: VERY FUTURE --> RUN REGRESSIONS.... HAIR FRIZZ+DEW POINT, FOR EX...
# TODO: VERY FUTURE --> HOW DIFF HAIR TYPES RESPOND TO WEATHER

# TODO: OUTPUT CURRENT CONDITIONS + FRIZZ ADVISORY
# TODO: MAYBE SAY WHY??? THE FRIZZ ADVISORY --> CONTRIBUTING FACTORS

# TODO: OPTIONAL, IF TIME REMAINS --> ADD FORECAST OPTION (THE DAY, 5 DAY, 10 DAY, ETC)

# TODO: OPTIONAL, IF TIME REMAINS --> HEROKU

# TODO: VERY IMPORTANT: ADD TESTS!!!!
# https://github.com/s2t2/stocks-app-py-2018/blob/master/tests/adviser_test.py

if __name__ == '__main__':

    location_name = "LOCATION NAME"
    def run_prog():
    # TODO: add emojis?!?!?! MAKE IT NICE I COOKED I CLEANED I MADE IT NICE
        print("----------")
        print("~ Hello and welcome to Frizzcaster! ~".upper())
        print("From local weather conditions, we predict the likelihood of frizz in your curls' future.\n")
        # TODO: have real user entry
        # location = input("Please enter the location you would like to check: ")


        location_key = location_key_by_ip()
        frizz_cast = forecast_range(location_key = location_key)

        print(location_name)

        # TODO: i wanted to make this its own function or take care of it in the other functitons, but return ends the loop
        for date, cast in frizz_cast.items():
            print(f"\n+ {date.upper()} FRIZZCAST +")
            if isinstance(cast, list):
                print(f"{cast[0].upper()} chance of frizz due to {cast[1]}!")
            else:
                print(f"{cast.upper()} chance of frizz!")

            # TODO: worth adding the why??? or removing??

        print(location_name)
        print("----------")
        print("")

        quit("\nThanks for using Frizzcast! Goodbye!")

        # make recurring if you have time --> more forecasts, location changes, or done


    # TODO: MAYBE CALL ALL FUNCTIONS HERE SO YOU DON'T NEED TO NEST THEM - IS CONUFUSING - LIKE CALLING DETECT_IP AND GET LOCATION AS RESULT


    # TODO: ask if user wants another forecast or another location (does this happen here or baked into function??)

    # TODO: make formatting for user inputs and the like better




run_prog()

# if __name__ == '__main__':


# VALUES
#
# + accu_hair_frizz +
# Unlikely: 0-2.99
# Watch: 3-4.99
# Advisory: 5-6.99
# Warning: 7-8.99
# Emergency: 9-10
#
# + dew_point +
# low/dry = <30 degrees f
# mid/ok - 30-40
# REALLY GOOD - 40-60
# high/BAD - 60-65
# BADBAD - 65-70
# UGHUGH - 70-75
# NOWAY - 75+
#
# + precipitation +
# override?
#
#
#
# + wind gusts +
# override?
#
#
#
# + temperature + just grab!!!
# + humidity + just grab!!!
#
# ORDER
# any precip will always lead to frizz
# crazy gusts of wind (over a certain number)
# dew point, segmented
#
# TODO: what is that stocks app error??
