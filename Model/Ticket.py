from datetime import datetime
from typing import List
from Model.Flight import Flight
from Model import SpecialOffer
class Ticket:
    def __init__(self, date_reservation: datetime, flight: Flight, seat_type: str, extra_luggage, specialoffers: List[SpecialOffer] = None):
        self.date_reservation = date_reservation
        self.flight = flight
        self.specialoffers = specialoffers or []
        self.seat_type = seat_type
        self.extra_luggage=extra_luggage
    def is_weekend(self):
        return self.date_reservation.isoweekday() > 5

    def is_advanced_booking(self):
        delta_days = (self.flight.date_departure - self.date_reservation).days
        return delta_days > 60
    def determine_price(self):
        from Service.GurobyResolver import dynamic_ticket_price
        return dynamic_ticket_price(self)


