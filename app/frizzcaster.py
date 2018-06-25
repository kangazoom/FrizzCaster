from dotenv import load_dotenv
import json
import os
import requests
from datetime import datetime
import pytest
from dateutil.parser import parse

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
    # when yes 200 response
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
    # when not 200 response status
        return "HTTP Error: " + str(e)

    if isinstance(response.text, str):
        response_text = json.loads(response.text)

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

# uses a user's ip address to automatically geolocate them
# returns accuweather location key if user agrees the location is accurate
# else sends user to choose_location function to manually define location (with country as parameter for greater accuracy)
# note: will throw error code 500 if ip address is invalid; except HTTP error from function parse_response
def location_key_by_ip():
    ip = detect_ip()
    request_url = f"http://dataservice.accuweather.com/locations/v1/cities/ipaddress?apikey={api_key}&q={ip}"
    response = requests.get(request_url)

    location = parse_response(response=response)
    global location_name

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
            location_name = f"{city}, {state}  {zip_code} {country}".upper()
            print("Great! We will use this location.")
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
    ask_location = True
    ask_decision = True

    while ask_location:

        location_input = input("Enter a city and state OR zip code: ".upper())
        global location_name

        request_url = f"http://dataservice.accuweather.com/locations/v1/search?apikey={api_key}&q={location_input}&offset=5"
        response = requests.get(request_url)
        locations = parse_response(response=response)


        if len(locations) >= 1:

            for location in locations:
            # prioritized location result will come from the country user is currently in
                if country == location["Country"]["EnglishName"]:
                    locations = location
                    break
            # in case user is accessing app from a different country from desired frizzcast location:
            if isinstance(locations, list):
                locations = locations[0]

            city = locations["EnglishName"]
            state = locations["AdministrativeArea"]["EnglishName"]
            country = locations["Country"]["EnglishName"]
            zip_code = locations["PrimaryPostalCode"]

            # NOTE: location_key is required to access local weather details
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
                    print("Great! We will use this location.")
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

# input: location_key (unique location code)
# user asked to choose forecast type and brought to the related function to grab forecast results
def forecast_range(location_key):

    while True:
        print("\n+ Select a FRIZZCAST from below +".upper())
        print("-----")
        print("[A] Right Now")
        print("[B] Today")
        print("[C] Five-Day Frizzcast")

        user_decision = input("\nEnter the letter indicating your choice: ").upper()
        print("----------")

        if user_decision == "A":
            return frizzcast_current(location_key)
        elif user_decision in ("B", "C"):
            return frizzcast_five(location_key, forecast_date = user_decision)
        else:
            print("Your selection was invalid. Let's try that again.")

# input from forecast_range(): location_key
# raw weather data is collected from relevant current conditions
# two functions interpret (1) the conditions into an advisory (2) the date and time into reader-friendly text
# output is CURRENT FORECAST dictionary with the results in {date:advisory} form
def frizzcast_current(location_key):
        request_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={api_key}&details=true"
        response = requests.get(request_url)
        current_forecast = parse_response(response=response)
        print("You want the frizzcast for right now!")

        if len(current_forecast) >= 1:

            observation_date_time = current_forecast[0]["LocalObservationDateTime"]

            dew_point_imperial = current_forecast[0]["DewPoint"]["Imperial"]["Value"]
            precipitation_imperial = current_forecast[0]["Precip1hr"]["Imperial"]["Value"]
            wind_speed_imperial = current_forecast[0]["Wind"]["Speed"]["Imperial"]["Value"]


            frizz_score = frizz_adviser_now(dew_point_imperial, precipitation_imperial, wind_speed_imperial)
            frizz_score = list(frizz_score)

            day_date_plus_time = time_readability(observation_date_time)

            results = {
            day_date_plus_time: frizz_score
            }

            print("\n ... current frizzcast ...")
            return results

        else:
            quit("Unexpected error.")

# input from forecast_range(): location_key + date range requested for forecast (today or five day)
# accuweather's hair frizz index is collected for a period of five days, beginning today
# two functions interpret (1) the index rating into an advisory (2) the date into reader-friendly text
# output is FORECAST FOR TODAY OR FIVE DAY FORECAST dictionary with the results in {date:advisory} form
def frizzcast_five(location_key, forecast_date):
    request_url = f"http://dataservice.accuweather.com//indices/v1/daily/5day/{location_key}/42?apikey={api_key}&details=true"
    response = requests.get(request_url)
    daily_forecast = parse_response(response=response)

    if len(daily_forecast) >= 1:

        today_forecast = daily_forecast.pop(0)
        five_day_forecast = daily_forecast

        if forecast_date == "B":
            # today only
            print("You want the frizzcast for today.")
            frizz_score = today_forecast["CategoryValue"]
            frizz_score = frizz_adviser_daily(frizz_score)

            day_date = today_forecast["LocalDateTime"]
            day_date = date_readability(day_date)

            result = {
            day_date: frizz_score
            }
            print("\n ... today's frizzcast ...")


        elif forecast_date == "C":
            # five days' worth
            print("You want the five-day frizzcast.")
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
            print("\n ... five-day frizzcast ...")

        return(result)

    else:
        quit("Unexpected error.")

# input: date and time as string
# string is transformed into datetime object
# output as readable string; ex: sunday june 24, 2018
def date_readability(day_date):
    day_date = parse(day_date)
    return day_date.strftime("%A %B %d, %Y")


# input: date and time as string
# string is transformed into datetime object
# output as readable string; ex: sunday june 24, 2018 at 02:06:00 pm
def time_readability(day_date_plus_time):
    day_date_plus_time = parse(day_date_plus_time)
    return day_date_plus_time.strftime("%A %B %d, %Y at %I:%M:%S %p")


# input: all imperial scales. dew point, precipitation, and wind speed
# THE SCALES : SYNTHESIZED INFO FROM VARIOUS HAIR BLOGS AND WEATHER WEBSITES
# output: advisory for CURRENT hair frizz + reason WHY
def frizz_adviser_now(dew_point, precipitation, wind_speed):

    # DEWPOINT SCALE
    if dew_point < 50:
        dew_point_scale = 1
    elif dew_point >= 50 and dew_point < 55:
        dew_point_scale = 2
    elif dew_point >= 55 and dew_point < 60:
        dew_point_scale = 3
    elif dew_point >= 60 and dew_point < 70:
        dew_point_scale = 4
    else:
        # when 70+ degrees F
        dew_point_scale = 5

    # PRECIPITATION SCALE (PREVIOUS HOUR)
    if precipitation <= 0:
        precipitation_scale = 1
    elif precipitation > 0 and precipitation < .098:
        precipitation_scale = 2
    elif precipitation >= .098 and precipitation < .3:
        precipitation_scale = 3
    elif precipitation >= .03 and precipitation < 2:
        precipitation_scale = 4
    else:
        # when 2+ inches
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
        # 24+ mph
        wind_speed_scale = 5

    high = "high"
    medium = "medium"
    low = "low"

    why_high_precipitation = "PRESENCE OF PRECIPITATION"
    why_high_wind = "UNUSUALLY STRONG WINDS"
    why_high_dewpoint = "HIGH DEWPOINT"
    why_medium_dewpoint = "MEDIUM DEWPOINT"
    why_low_dewpoint = "LOW DEWPOINT"
    why_low_wind = "CALM WINDS"
    why_low_precipitation = "LITTLE TO NO PRECIPITATION"


    if precipitation_scale > 1 and dew_point_scale in (4, 5):
        return(high, why_high_precipitation, why_high_dewpoint)
    elif wind_speed_scale == 5 and dew_point_scale in (4, 5):
        return(high, why_high_wind, why_high_dewpoint)
    elif precipitation_scale > 1 and wind_speed_scale == 5:
        return(high, why_high_precipitation, why_high_wind)
    elif precipitation_scale > 1:
        return(high, why_high_precipitation)
    elif wind_speed_scale == 5:
        return(high, why_high_wind)
    elif dew_point_scale in (4, 5):
        return(high, why_high_dewpoint)
    elif dew_point_scale == 3:
        return(medium, why_medium_dewpoint)
    else:
        # dew point is scale 1; no precipitation; calm winds
        return(low, why_low_dewpoint, why_low_precipitation, why_low_wind)

# input: takes hair frizz category-level indices from AccuWeather
# output: advisory for THE DAY'S hair frizz
# NOTE for future: get 120 hour forecast for better predictions (this is premium for most weather apis...)
def frizz_adviser_daily(frizz_score):
    high = "high"
    medium = "medium"
    low = "low"

    if frizz_score <= 1:
        return(low)
    elif frizz_score > 1 and frizz_score < 4:
        return(medium)
    else:
        # is 4 or 5
        return(high)

# i made this a global variable b/c it is never returned, but i want to use again over different functions
location_name = "YOUR LOCATION"

# this function runs all of the other functions
# no parameters or returns; is that ok??
def run_prog():
    print("----------")
    print("~ Hello and welcome to Frizzcaster! ~".upper())
    print("From local weather conditions, we predict the likelihood of frizz in your curls' future.\n")

    # run all the location-related functions until we get a location user is happy with
    location_key = location_key_by_ip()
    # run all the forecast-related functions
    frizz_cast = forecast_range(location_key = location_key)

    print(f"** {location_name} **")

    # TODO: current - what if 3 items returned: frizzcast, why_precipitation, why_high_dewpoint

    for date, cast in frizz_cast.items():
        print(f"\n+ {date.upper()} FRIZZCAST +")
        if isinstance(cast, list):
        # current frizzcast will include advisory + reason(s) why
            if len(cast) == 4:
                print(f"{cast[0].upper()} chance of frizz due to {cast[1].upper()}, {cast[2].upper()}, and {cast[3].upper()}!")
            elif len(cast) == 3:
                print(f"{cast[0].upper()} chance of frizz due to {cast[1].upper()} and {cast[2].upper()}!")
            else:
                print(f"{cast[0].upper()} chance of frizz due to {cast[1].upper()}!")
        else:
        # daily-type forecasts will only have advisory
            print(f"{cast.upper()} chance of frizz!")

    print("----------")

    quit("\nThanks for using Frizzcast! Goodbye!\n")


if __name__ == '__main__':
    run_prog()
