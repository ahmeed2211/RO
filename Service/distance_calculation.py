import requests
import math

def get_latlng(country):
    url = f"https://restcountries.com/v3.1/name/{country}?fields=latlng"
    data = requests.get(url).json()
    return data[0]["latlng"]

def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def distance_between_countries(country1, country2):
    lat1, lon1 = get_latlng(country1)
    lat2, lon2 = get_latlng(country2)
    return calculate_distance_km(lat1, lon1, lat2, lon2)

