import argparse
import pathlib
import json
from FlightSchedule import FlightSchedule
from datetime import datetime, timedelta


def json_serialize(obj):
    """helper function to json serialize datetime to isostrings"""

    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def parse_timedelta(s):
    """helper function to parse interval data from string"""
    
    t = datetime.strptime(s, "%H:%M")
    return timedelta(hours=t.hour, minutes=t.minute)


# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("filepath", help="path to csv file",
                    type=pathlib.Path)
parser.add_argument("origin", help="origin airport",
                    type=str.upper)  # convert to uppercase for convenience
parser.add_argument("destination", help="destination airport",
                    type=str.upper)  # convert to uppercase for convenience
parser.add_argument("--bags", help="number of bags",
                    type=int, default=0)
parser.add_argument("--return_flight", help="search return flights",
                    action="store_true")
parser.add_argument("--alt_origins", help="alternative origin airports",
                    nargs="*", type=str.upper, default=[])  # convert to uppercase for convenience
parser.add_argument("--alt_destinations", help="alternative destination airports",
                    nargs="*", type=str.upper, default=[])  # convert to uppercase for convenience
parser.add_argument("--return_to_other_airport", 
                    help="return journey's destination can be other than outbound journey's origin",
                    action="store_true")
parser.add_argument("--return_from_other_airport", 
                    help="return journey's origin can be other than outbound journey's destination",
                    action="store_true")
parser.add_argument("--min_transfer_time", help="minimal transfer time (HH:MM)",
                    type=parse_timedelta, default="01:00")
parser.add_argument("--max_transfer_time", help="maximal transfer time (HH:MM)",
                    type=parse_timedelta, default="06:00")
parser.add_argument("--min_days_at_destination", help="minimal number of days at destination",
                    type=int, default=0)
parser.add_argument("--max_days_at_destination", help="maximal number of days at destination",
                    type=int)
parser.add_argument("--min_departure", help="minimal departure datetime",
                    type=datetime.fromisoformat)
parser.add_argument("--max_departure", help="maximal departure datetime",
                    type=datetime.fromisoformat)
parser.add_argument("--max_transfers", help="maximal number of transfers",
                    type=int)
args = parser.parse_args()

flight_schedule = FlightSchedule()

# load flight schedule from csv file
if args.filepath.exists():
    flight_schedule.load_from_csv(args.filepath)
else:
    raise FileNotFoundError(f"File does not exist {args.filepath}")

# run the search engine
results = flight_schedule.search(origins=[args.origin]+args.alt_origins, 
                                 destinations=[args.destination]+args.alt_destinations,
                                 bags=args.bags, 
                                 return_flight=args.return_flight,
                                 return_to_other_airport=args.return_to_other_airport,
                                 return_from_other_airport=args.return_from_other_airport,
                                 min_transfer_time=args.min_transfer_time,
                                 max_transfer_time=args.max_transfer_time,
                                 min_days_at_destination=args.min_days_at_destination,
                                 max_days_at_destination=args.max_days_at_destination,
                                 min_departure=args.min_departure,
                                 max_departure=args.max_departure,
                                 max_transfers=args.max_transfers,
                                 sort_by=['total_price', 'departure', 'travel_time'])

# transform our results into a list of dictionaries
dict_results = [trip.to_dict() for trip in results]

# transform our results into requested json format
# we need to take care of datetime fields and transform them back to iso strings
json_results = json.dumps(dict_results, indent=4, default=json_serialize)
print(json_results)
