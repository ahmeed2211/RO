from Model.Airline import *
from Service.determine_holidays import exist_holidays
from Service.determine_tourist_attraction import *
from Service.stops_estimation import estimate_stops, choose_aircraft
from datetime import datetime

from constants.Airline_Specific_Constants.Base_Aircraft_Cost import BASE_AIRCRAFT_COST
from constants.Airline_Specific_Constants.Base_Seat_Cost import BASE_SEAT_PRICE
from constants.Airline_Specific_Constants.Seat_Types import SeatTypes
import os
import json
from QtDesigner import *


def load_settings():
    """Simple version assuming QtDesigner is in Python path"""
    try:
        # Get the directory of the QtDesigner package
        import QtDesigner
        import inspect

        # Get the file path of the QtDesigner __init__.py
        package_file = inspect.getfile(QtDesigner)
        package_dir = os.path.dirname(os.path.abspath(package_file))

        # Construct path to settings.json
        settings_path = os.path.join(package_dir, 'settings.json')

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                print(f"Successfully loaded settings from: {settings_path}")
                return settings
        else:
            print(f"settings.json not found at: {settings_path}")

    except Exception as e:
        print(f"Error loading settings: {e}")

    return {}


class Flight:
    def __init__(self, date_departure, date_return , from_country, to_country ,airline_name="SkyHigh Airline"):
        self.distance,self.aircraft = choose_aircraft(from_country, to_country)
        self.airline = Airline(airline_name)
        self.date_departure = self._parse_date(date_departure)
        self.date_return = self._parse_date(date_return) if date_return else None
        self.from_country = from_country
        self.to_country = to_country
        self.sold_seats = 0
        self.max_seats = self.aircraft["capacity"]
        self.settings = load_settings()
        print(self.settings)
        # dynamic base seat prices — no hardcoding outside
        self.seat_base_price = {
            "economic": float(self.settings["base_price"]) * float(self.settings["economy_factor"]) *self.airline.airline_efficiency ,
            "Premium Economy" : float(self.settings["base_price"] ) * float(self.settings["premium_economy_factor"])  *  self.airline.airline_efficiency,
            "business":float(self.settings["base_price"])  * float(self.settings["business_factor"]) * self.airline.airline_efficiency,
            "first": float(self.settings["base_price"])  * float(self.settings["first_class_factor"]) * self.airline.airline_efficiency,
        }
        self.stops= estimate_stops(self.to_country,self.from_country)
    def is_holiday_period(self):
        if exist_holidays(self.to_country, self.date_departure, self.date_return):
            return True
        return False
    def _get_efficiency(self):
        return self.settings["efficiency"]
    def _parse_date(self, date):
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d')
        elif isinstance(date, datetime):
            return date
        else:
            raise ValueError("Date must be a string in 'YYYY-MM-DD' format or a datetime object")
    def touristDeftination(self):
        return classify_tourism(self.from_country)

    def to_string(self):
        return f"Flight from {self.from_country} to {self.to_country} " \
               f"departing on {self.date_departure.strftime('%Y-%m-%d')} " \
               f"returning on {self.date_return.strftime('%Y-%m-%d')} via {self.airline.airline_name}"\
               f" and stops_estimated {self.determine_stops()}"
    def determinedemande(self):
        demande=0
        if (exist_holidays(self.to_country)) :
            demande+=0.2
        if (classify_tourism(self.to_country == LOW_TOURIST_DESTINATION)) :
            demande+=0
        if(classify_tourism(self.to_country) == MODERATE_TOURIST_DESTINATION) :
            demande+=0.1
        if (classify_tourism(self.to_country) == STRONG_TOURIST_DESTINATION) :
            demande+=0.2
        if (classify_tourism(self.to_country) == MAJOR_TOURIST_DESTINATION) :
            demande+=0.3

    def destiation_is_tourist_hotspot(self):
        if(classify_tourism(self.to_country) == MAJOR_TOURIST_DESTINATION or classify_tourism(self.to_country) == STRONG_TOURIST_DESTINATION):
            return True
        return False



    def determine_cost(self):
        return BASE_AIRCRAFT_COST * self.aircraft["cost_factor"]
    def determine_stops(self):
        return estimate_stops(self.to_country,self.from_country)
    def valid(self):
        if self.from_country==self.to_country :
            print("can't fly within the same country")
            return
        if self.date_return< self.date_departure:
            print("date return must be greater than date departure")
            return
        return True
