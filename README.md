# Python weekend entry task - submission by David Nádhera

## Files structure

| File name           |  Description              												   |
|---------------------|----------------------------------------------------------------------------------------------------------------------------|
| `search.py`         |  Main runnable module that loads csv file, performs search according to parameters and outputs the results in json format  |
| `Trip.py` 	      |  Class representing a group of consecutive flights									   |
| `FlightSchedule.py` |  Class representing flight schedule											   |


## Running instructions

We run the search by command

```
python -m search <path_to_csv_file> <XXX> <YYY>
```

where `<path_to_csv_file>` is path to csv file with flights data, `<XXX>` is code of origin airport and `<YYY>` is code of destination airport. Python version 3.10 is required. 

### Required arguments

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `filepath`    | string  | Path to csv file         | Required                     |
| `origin`      | string  | Origin airport code      | Required                     |
| `destination` | string  | Destination airport code | Required                     |

### Optional arguments

| Argument name               | type     | Description             		 								| Notes                        		    |
|-----------------------------|----------|------------------------------------------------------------------------------------------------------|-------------------------------------------|
| `bags`                      | integer  | Number of requested bags 		 								| defaults to 0     			    |
| `return_flight`             | boolean  | Is it a return flight?   		 								| defaults to false 			    |
| `alt_origins`               | string   | Alternative origin airport codes   									| defaults to None, multiple values allowed |
| `alt_destinations`          | string   | Alternative destination airport codes   								| defaults to None, multiple values allowed |
| `return_to_other_airport`   | boolean  | In case of return flight and more possible origin airports, can we return to different one?   	| defaults to false 			    |
| `return_from_other_airport` | boolean  | In case of return flight and more possible destination airports, can we return from different one?   | defaults to false 			    |
| `min_transfer_time` 	      | interval | Minimal allowed transfer time (HH:MM)  								| defaults to 01:00 			    |
| `max_transfer_time` 	      | interval | Maximal allowed transfer time (HH:MM)  								| defaults to 06:00 			    |
| `min_days_at_destination`   | int      | In case of return flights, minimal number of days before flight back   				| defaults to 0 			    |
| `min_days_at_destination`   | int      | In case of return flights, maximal number of days before flight back   				| defaults to unlimited 		    |
| `min_departure`             | datetime | Departure must be after this date/time   								| defaults to unlimited 		    |
| `max_departure`             | datetime | Departure must be before this date/time   								| defaults to unlimited 		    |
| `max_transfers`             | int      | Maximum number of transfers (on way there or back)  	 						| defaults to unlimited 		    |

### Example

Example command using all possible parameters

```
python -m search example/example3.csv WUE ZRW --bags 1 --return_flight --alt_origins EZO VVH --alt_destinations JBN --return_to_other_airport --return_from_other_airport --min_transfer_time 00:45 --max_transfer_time 08:00 --min_days_at_destination 5 --max_days_at_destination 8 --min_departure 2021-09-02T00:00:00 --max_departure 2021-09-09T00:00:00 --max_transfers 2
```

## Implementation

The flights data are stored into dictionary indexed by origin airport of the flight. Values are lists of flights departing from that airport ordered by departure time. This way we can quickly find all flights departing from each airport in a given timeframe.

Searching is implemented by deep first search algorithm. Our task is to find all possible combinations so we have to traverse all combinations anyway but at least it is more economical from memory point of view.

### Possible uncertainties

- In case of return flight, what to put into `destination` field of the trip? The destination of the query or real destination of the whole trip which is usually same as origin. It would probably be better to separate outbound and return journey of the trip but I had to follow the specification. I decided to choose the latter. Doing the other way would require only a small change in code.

- When allowing multiple origin airports, it is not clear whether to allow visits of other origin airports during the trip. For example if we search flights from Prague or Vienna, do we allow to start the trip by Prague-Vienna flight or to visit Vienna later on a trip originating in Prague? I decided not to allow this, however allowing this would be easy as well

- The same for returning flight with multiple destination airports and option to return back from different airport













