import math

from Service.distance_calculation import distance_between_countries
from Model.Aircraft_types import AIRCRAFT_TYPES



def choose_aircraft (country1, country2) :
    distance = distance_between_countries(country1, country2)
    if distance <= 2500:
        aircraft = AIRCRAFT_TYPES["narrow"]
    elif distance <= 5000:
        aircraft = AIRCRAFT_TYPES["extended"]
    elif distance <= 10000:
        aircraft = AIRCRAFT_TYPES["long"]
    else:
        aircraft = AIRCRAFT_TYPES["ultra"]

    return distance, aircraft


def estimate_stops(country1, country2) :
    distance, aircraft = choose_aircraft(country1, country2)
    range_ = aircraft["range"]

    segments = math.ceil(distance / range_)
    return max(0, segments - 1)

print(choose_aircraft("Brazil", "Japan"))