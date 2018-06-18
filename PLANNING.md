# Project Planning

## Primary User
The primary user is a person with curly hair whose hair tends to turn frizzy under certain weather conditions.

## Problem Statement
It can be confusing and difficult for a person with curly hair to figure out how to take care of their hair. Certain weather conditions play a huge role in what a person's hair will look like for that day. While people with curly hair have different textures and thus respond differentially to the weather, most curly-haired folks dislike how humidity affects their locks. However, hair chemists point to more complex factors as the culprits:  namely, dew point. Thus, it would be helpful to quickly and accurately determine what kind of "hair" day it will be.

## As-Is Process Description
1. View weather website in browser or from mobile app (ex: wunderground.com)
2. View the day's relative humidity
3. Check for rain
4. Alter hair routine based on incomplete information

## To-Be Process Description
1. Enter location
2. Receive hair frizz advisory

## Information Requirements

### Information Inputs
1. User's desired zip code (NOTE: for greater accuracy, might also allow user to enter name of city name or find a module to geolocate user)
2. *Maybe also: desired forecast range (ex: current moment only or also one-day + ten-day)*


### Information Outputs
1. Hair frizz advisory (low-->high), given current weather conditions
2. Reasoning (based mainly on dew point, but also add temperature, humidity, precipitation--maybe also wind and/or air pressure)
3. *Maybe also: Extended forecast (ex: one-day + ten-day)*


## Technology Requirements

### APIs and Web Service Requirements

I will use the [Accuweather API] (https://developer.accuweather.com/). Interestingly, they have their own hair frizz index, but do not reveal how they arrived at this metric. I will need to decide if I should rely on it (as it is a complete black box) or create my own.

Accuweather's API does limit the number of free requests I can make per day to fifty. If we foresee this as an issue, then I could instead use:
- *[Darksky API] (https://darksky.net/dev)*
- *[Weatherbit API] (https://www.weatherbit.io/api)*
- *[ClimaCell API] (https://developer.climacell.co/)*

### Python Package Requirements

1. dotenv for the API key's security
2. json to parse data
3. requests to interact with the API
4. pytest for testing purposes
5. *possibly also [geocoder] (http://geocoder.readthedocs.io/) to geolocate user*

### Hardware Requirements

I will run the program from my laptop, although I would love to put it up on heroku one day.
