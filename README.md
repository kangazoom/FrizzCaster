# freestyle-app

## frizzcaster.py

### FRIZZCASTER
This app tells curly-haired users the likelihood of frizzy hair in their forecast.

### Installation
- Fork [this respository](https://github.com/kangazoom/freestyle-app) under your own control.
- Download your forked version of this repository using the GitHub.com online interface or the Git command line interface.
- Using command line Git, you can download it by "cloning" it:
'''
git clone git@github.com:kangazoom/freestyle-app.git
cd freestyle-app
'''

- Install package dependencies using one of the following commands, depending on how you have installed Python and how you are managing packages:

'''
# Pipenv on Mac or Windows:
pipenv install -r requirements.txt

# Homebrew-installed Python 3.x on Mac OS:
pip3 install -r requirements.txt

# All others:
pip install -r requirements.txt
'''

### Setup
- Register and obtain an API key from [AccuWeather](https://developer.accuweather.com/).
- Add the following to a .env file:
'''
ACCUWEATHER_API_KEY=[plug in your API key]
'''
- Or add it to your .bash_profile by adding the following line:
'''
export ACCUWEATHER_API_KEY=[plug in your API key]
'''

Note that under an unpaid account, you are limited to fifty requests per day.


### Usage
Execute the frizzcaster.py app from your command line:

'''
# Homebrew-installed Python 3.x on Mac OS, not using Pipenv:
python3 app/frizzcaster.py

# All others, including Pipenv on Mac or Windows:
python app/frizzcaster.py
'''

### Testing
Test cases exist in the freestyle-app/tests directory.
,,,
cd freestyle-app/tests
pytest
'''

### [License](http://kangazoom/freestyle-app/license)
