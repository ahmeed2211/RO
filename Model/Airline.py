from constants.AIRLINES import AIRLINES


class Airline:
    def __init__(self, airline_name):
        self.airline_name = airline_name
        if airline_name in AIRLINES:
            self.airline_efficiency= AIRLINES[airline_name]["efficiency"]



