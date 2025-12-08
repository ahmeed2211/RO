from wsgiref.headers import Headers

import requests
from datetime import datetime, timedelta

from Service.distance_calculation import get_latlng


def get_holidays(country, api_key = "47N0J3bFDkwFUaYJTWtYTKjRzAUhIkvs7SF5pCDL") :
    lat, lon = get_latlng(country)
    url = f"https://api.api-ninjas.com/v1/holidays?country={country}&type=public_holiday"
    Headers ={
        "x-api-key" : api_key }
    data = requests.get(url, headers= Headers).json()
    return data

def exist_holidays(country, date_departure, date_retour):
    holidays = get_holidays(country)

    for holiday in holidays:
        holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
        if  date_departure.date() <= holiday_date <= date_retour.date() :
            print(holiday_date)
            return True
    return False


