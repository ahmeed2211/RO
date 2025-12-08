import requests
from Service.IsoCountry import *
from constants.tourism_constants import *

def number_arrivals(country) :
    isocountrycode= get_isocode(country)
    if isocountrycode is None :
        isocountrycode = country
    url=f"https://api.worldbank.org/v2/country/{isocountrycode}/indicator/ST.INT.ARVL?format=json"
    data = requests.get(url).json()
    indicators = data[1]
    print(indicators)
    for indicator in indicators :
        if indicator["value"] is not None :
            return indicator["value"]

    return 0

def country_rank (country) :
    countries_dict={}
    for country in IsoCountry :
        x = number_arrivals(country)
        print(x)
        countries_dict[country] = x

    rank_countries = dict(sorted(countries_dict.items(), key=lambda x: x[1], reverse=True))

    return rank_countries


def classify_tourism(country):
    arrivals = number_arrivals(country)
    if arrivals is None:
        return NO_DATA

    if arrivals > 10_000_000:
        return MAJOR_TOURIST_DESTINATION
    elif arrivals > 3_000_000:
        return STRONG_TOURIST_DESTINATION
    elif arrivals > 1_000_000:
        return MODERATE_TOURIST_DESTINATION
    else:
        return LOW_TOURIST_DESTINATION
