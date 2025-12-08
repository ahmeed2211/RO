from constants.Airline_Specific_Constants.Seat_Types import SeatTypes

class Seat:
    def __init__(self, name):
        self.name = name
        if name in SeatTypes:
            self.additionalfees= SeatTypes[name]


