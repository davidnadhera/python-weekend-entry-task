import csv
from datetime import datetime, timedelta
import bisect
from Trip import Trip


class FlightSchedule:
    MIN_TRANS_TIME = timedelta(hours=1)
    MAX_TRANS_TIME = timedelta(hours=6)

    def __init__(self):
        self._flight_schedule = {}

    def load_from_csv(self, filepath):
        """ load flight schedule from csv file into a dictionary where keys are origin airports
            and values are lists of all flights departing from these airports ordered by
            departure time

            PARAMS: filepath (str) - path to csv file"""

        required_fields = ['departure', 'arrival', 'base_price', 'bag_price', 'bags_allowed', 'origin', 'destination']

        self._flight_schedule.clear()
        with open(filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # validate whether csv has all required columns
            if any([field not in reader.fieldnames for field in required_fields]):
                raise IOError('CSV file does not have correct format.')
            for row in reader:
                # convert datetime fields
                row['departure'] = datetime.fromisoformat(row['departure'])
                row['arrival'] = datetime.fromisoformat(row['arrival'])
                # convert numerical fields
                row['base_price'] = float(row['base_price'])
                row['bag_price'] = float(row['bag_price'])
                row['bags_allowed'] = int(row['bags_allowed'])
                # store flights into dictionary indexed by origin airport, so we can quickly find all flights
                # departing from each airport
                if row['origin'] not in self._flight_schedule:
                    self._flight_schedule[row['origin']] = []
                self._flight_schedule[row['origin']].append(row)

        # sort list of departures from each airport by departure time
        for origin in self._flight_schedule:
            self._flight_schedule[origin].sort(key=lambda x: x['departure']) 

    def get_departing_flights(self, origin, time_from=None, time_to=None, bags_count=None,
                              excluded_destinations=None):
        """ get all flights departing from origin

            PARAMS: origin (str)- code of origin airport
                    time_from (datetime, optional) - earliest datetime of departure
                    time_to (datetime, optional) - latest datetime of departure
                    bags_count (int, optional) - flight must allow at least this count of bags
                    excluded_destinations (list, optional) - list of codes of destination airports
                        to be excluded
            RETURN: list of flights"""

        if origin not in self._flight_schedule:
            return []
        departing_flights = self._flight_schedule[origin]
        if time_from is not None:
            # choose only flights with departure later than time_from
            i = bisect.bisect_left(departing_flights, time_from, key=lambda x: x['departure'])
            departing_flights = departing_flights[i:]
        if time_to is not None:
            # choose only flights with departures earlier than time_to
            i = bisect.bisect_right(departing_flights, time_to, key=lambda x: x['departure'])
            departing_flights = departing_flights[:i]
        if bags_count is not None:
            # filter out flights with insufficient bags allowance
            departing_flights = \
                [flight for flight in departing_flights if flight['bags_allowed'] >= bags_count]
        if excluded_destinations is not None:
            # filter out excluded destinations
            departing_flights = \
                [flight for flight in departing_flights if flight['destination'] not in excluded_destinations]
        return departing_flights 

    def search(self, origins, destinations, bags=0, sort_by=None,
               return_flight=False, return_to_other_airport=False, return_from_other_airport=False,
               min_transfer_time=MIN_TRANS_TIME, max_transfer_time=MAX_TRANS_TIME,
               min_days_at_destination=0, max_days_at_destination=None, min_departure=None, max_departure=None,
               max_transfers=None):
        """ Search all flights according to parameters and return them as list of trips in sorted in specified order

            PARAMS: origins (list) - list of codes of origin airports
                    destinations (list) - list of codes of destination airports
                    bags (int) - number of bags carried (default 0)
                    sort_by (list) - list of trip attributes specifying the order of results
                                     (default total_price,departure,travel_time)
                    return_flight (bool) - is it a return flight? (default False)
                    return_to_other_airport (bool) - in case of multiple origin airports, return
                                                     flight can be to different one (default False)
                    return_from_other_airport (bool) - in case of multiple destination airports,
                                                       return flight can be from different one
                                                       (default False)
                    min_transfer_time (timedelta) - minimal allowed transfer time (default 1 hour)
                    max_transfer_time (timedelta) - maximal allowed transfer time (default 6 hours)
                    min_days_at_destination (int) - minimal number of days before return flight (default 0)
                    max_days_at_destination (int, optional) - maximal number of days before return flight
                    min_departure (datetime, optional) - the earliest allowed departure from origin airport
                    max_departure (datetime, optional) - the latest allowed departure from origin airport
                    max_transfers (int, optional) - maximal number of transfers (separate for outbound and return
                                                    journey
            RETURN: list of trips in specified order
        """

        def dfs(trip, visited):  # deep first search - outbound journey
            results = []
            if trip.destination in destinations:
                # we reached final destination of outbound journey, finish the trip
                return [trip]
            elif (max_transfers is None) or (len(visited) <= max_transfers + 1):
                # we have some available transfers left
                # get all connecting flights with respect to transfer times to a destination not visited so far
                # we don't want to transfer at another origin airport because we could easier start our journey there
                excluded_destinations = origins + visited 
                if len(visited) == 1:  # first flight in trip
                    time_from = min_departure
                    time_to = max_departure
                else:  # transfer
                    time_from = trip.arrival+min_transfer_time
                    time_to = trip.arrival+max_transfer_time
                departing_flights = self.get_departing_flights(trip.destination, 
                                                               time_from=time_from,
                                                               time_to=time_to,
                                                               bags_count=bags,
                                                               excluded_destinations=excluded_destinations)
                for flight in departing_flights:  # search all possible connections
                    new_trip = trip.add_flight(flight)
                    new_visited = visited.copy()
                    new_visited.append(flight['destination'])
                    results.extend(dfs(new_trip, new_visited))
            
            return results
    
        def dfs_back(trip, visited):  # deep first search - return journey
            results = []
            if trip.destination == trip.origin:  # we are back at origin, finish the trip
                return [trip]
            elif return_to_other_airport and (trip.destination in origins):
                # we don't need to return to the same airport, finish the trip
                return [trip]
            elif (max_transfers is None) or (len(visited) <= max_transfers + 1):
                # we have some available transfers left
                # get all connecting flights with respect to transfer times to a destination not visited so far
                # if we can return from another airport, we don't want to transfer at another destination airport 
                # because we could easier start our journey there
                excluded_destinations = destinations + visited if return_from_other_airport else visited
                if len(visited) == 1:  # first flight of return journey
                    time_from = trip.arrival+timedelta(days=min_days_at_destination)
                    time_to = \
                        None if max_days_at_destination is None \
                        else trip.arrival+timedelta(days=max_days_at_destination)
                else:  # transfer
                    time_from = trip.arrival+min_transfer_time
                    time_to = trip.arrival+max_transfer_time
                departing_flights = self.get_departing_flights(trip.destination, 
                                                               time_from=time_from,
                                                               time_to=time_to,
                                                               bags_count=bags,
                                                               excluded_destinations=excluded_destinations)
                for flight in departing_flights:  # search all possible connections
                    new_trip = trip.add_flight(flight)
                    new_visited = visited.copy()
                    new_visited.append(flight['destination'])
                    results.extend(dfs_back(new_trip, new_visited))
            
            return results

        # check if all airport codes exist and whether origin and destination airports do not overlap
        for origin in origins:
            if origin not in self._flight_schedule:
                raise KeyError(f'Unknown airport code {origin}')
        for destination in destinations:
            if destination not in self._flight_schedule:
                # we assume here that there won't be any airport with arriving flights only
                raise KeyError(f'Unknown airport code {destination}')
        if set(origins).intersection(destinations):
            raise ValueError('Origins and destinations are overlapping.')

        results = []
        for origin in origins:
            trip = Trip(origin, bags)
            results = dfs(trip, [origin])
       
        if return_flight:  # search flights back if it is a return flight query
            outbound_results = results
            results = []
            # if we can return from different airports we create a copy for each possible combination of
            # outbound trip and destination airport
            for trip in outbound_results:
                if return_from_other_airport:
                    for destination in destinations:
                        trip.destination = destination
                        results.extend(dfs_back(trip, [destination]))
                else:
                    results.extend(dfs_back(trip, [trip.destination]))

        # sort results in order defined by sort_by argument
        # it can be useful to be able to sort by other field(s) in future
        if sort_by is not None:
            results.sort(key=lambda x: tuple(getattr(x, key, 0) for key in sort_by))

        return results
