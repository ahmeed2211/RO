from constants.Airline_Specific_Constants.AIRCRAFT_TYPES import AIRCRAFT_TYPES

class Aircraft:
    def __init__(self, aircraft_type):
        self.aircraft_type = aircraft_type
        if aircraft_type in AIRCRAFT_TYPES :
            self.name = AIRCRAFT_TYPES [aircraft_type]["name"]
            self.range =AIRCRAFT_TYPES [aircraft_type]["range"]
            self.capacity = AIRCRAFT_TYPES [aircraft_type]["capacity"]
            self.cost_factor = AIRCRAFT_TYPES [aircraft_type]["cost_factor"]
        else:
            self.name = None
            self.range = None
            self.capacity = None
            self.cost_factor = None
