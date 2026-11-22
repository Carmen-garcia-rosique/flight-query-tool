"""Row validation: airport list loading, single-row checks, record building."""
import re
from datetime import datetime

import math

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if code and not code.startswith("#"):
                airports.add(code)

    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    # Check 1: The row must contain exactly 6 fields
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    # Remove spaces from each field
    fields = [field.strip() for field in fields]

    # Check 2: No field can be empty
    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    # Check 3: Validate flight ID
    flight_id = fields[0]

    if not (2 <= len(flight_id) <= 8):
        return "INVALID_FLIGHT_ID"

    if not all(char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for char in flight_id):
        return "INVALID_FLIGHT_ID"

    # Check 4: Validate origin airport
    origin = fields[1]

    if len(origin) != 3 or not all("A" <= char <= "Z" for char in origin) or origin not in airports:
        return "INVALID_ORIGIN"

    # Check 5: Validate destination airport
    destination = fields[2]

    if len(destination) != 3 or not all("A" <= char <= "Z" for char in destination) or destination not in airports:
        return "INVALID_DESTINATION"

    # Check 6: Origin and destination must be different
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # Check 7: Validate departure datetime
    departure = fields[3]
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"

    if not re.fullmatch(date_pattern, departure, flags=re.ASCII):
        return "INVALID_DEPARTURE"

    try:
        departure_date = datetime.strptime(departure, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_DEPARTURE"

    # Check 8: Validate arrival datetime
    arrival = fields[4]

    if not re.fullmatch(date_pattern, arrival, flags=re.ASCII):
        return "INVALID_ARRIVAL"

    try:
        arrival_date = datetime.strptime(arrival, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_ARRIVAL"

    # Check 9: Arrival must be after departure
    if arrival_date <= departure_date:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # Check 10: Price must be a valid finite number
    price = fields[5]

    try:
        price_value = float(price)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    # Check 11: Price must be positive
    if price_value <= 0:
        return "NON_POSITIVE_PRICE"


    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields [0],
        "origin": fields [1],
        "destination": fields [2],
        "departure_datetime": fields [3],
        "arrival_datetime": fields [4],
        "price": float(fields[5])
    }
