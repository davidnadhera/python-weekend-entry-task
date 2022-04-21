import copy
from datetime import timedelta


class Trip:
    """ sequence of connecting flights

        ATTRIBUTES: origin (str) - code of origin airport
                    destination (str) - code of destination airport
                    flights (list) - list of flights data
                    total_price (float) - total price of all flights including bags
                    departure (datetime) - datetime of departure
                    arrival (datetime) - datetime of arrival
                    travel_time (timedelta) - total travel time between departure and arrival
                    bags_count (int) - number of bags carried
                    bags_allowance (int) - maximal bags allowance of whole trip
    """

    def __init__(self, origin, bags):
        """ initialize trip with empty trip and set number of bags carried

            PARAMS: origin (str) - code of origin airport
                    bags (int) - number of bags carried
        """

        self.origin = origin
        self.destination = origin
        self.flights = []
        self.total_price = 0.0
        self.departure = None
        self.arrival = None
        self.travel_time = timedelta(0)
        self.bags_count = bags
        self.bags_allowed = None

    def add_flight(self, flight):
        """ Add connecting flight to current trip

            PARAMS: flight (dict) - flight data of connecting flight
            RETURN: copy of a trip with connecting flight added
        """

        if flight['origin'] != self.destination:
            raise ValueError(f"Arrival and departure airports do not match {self.destination}, {flight['origin']}")
        if flight['bags_allowed'] < self.bags_count:
            raise ValueError(f"Number of bags exceeds bags allowance {self.bags_count}, {flight['bags_allowed']}")
            
        new_trip = self.copy()
        new_trip.destination = flight['destination']
        new_trip.flights.append(flight)
        new_trip.total_price += flight['base_price'] + self.bags_count * flight['bag_price']
        if self.departure is None:
            new_trip.departure = flight['departure']
        new_trip.arrival = flight['arrival']
        new_trip.travel_time = new_trip.arrival - new_trip.departure
        new_trip.bags_allowed = \
            flight['bags_allowed'] if self.bags_allowed is None else min(flight['bags_allowed'], self.bags_allowed)
        return new_trip 

    def to_dict(self):
        """ returns trip data in a form of dictionary"""

        return {'flights': self.flights,
                'bags_allowed': self.bags_allowed,
                'bags_count': self.bags_count,
                'destination': self.destination,
                'origin': self.origin,
                'total_price': self.total_price,
                'travel_time': str(self.travel_time)} 

    def copy(self):
        """ does a semi-deep copy including its own copy of list of flights but excluding each flight itself"""

        new_trip = copy.copy(self)
        new_trip.flights = self.flights.copy()
        return new_trip   
