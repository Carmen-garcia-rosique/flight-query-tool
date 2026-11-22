"""Running queries against the flight database."""
import re
import math 
from datetime import datetime

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """

    allowed_keys = {
        "flight_id", "origin", "destination",
        "departure_datetime", "arrival_datetime",
        "price", "min_price", "sort_by", "order", "limit"
    }

    if not isinstance(query, dict):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for key in query:
        if key not in allowed_keys:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # Validate string filters
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # Validate datetime filters
    date_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            value = query[key]

            if not isinstance(value, str) or not re.fullmatch(date_pattern, value):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # Validate numeric filters
    for key in ("price", "min_price"):
        if key in query:
            value = query[key]

            if type(value) not in (int, float) or not math.isfinite(value):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # Validate sorting
    record_keys = {
        "flight_id", "origin", "destination",
        "departure_datetime", "arrival_datetime", "price"
    }

    if "sort_by" in query and (
    not isinstance(query["sort_by"], str)
    or query["sort_by"] not in record_keys
):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "order" in query:
        if (
            "sort_by" not in query
            or not isinstance(query["order"], str)
            or query["order"] not in ("asc", "desc")
        ):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    # Validate result limit
    if "limit" in query:
        if type(query["limit"]) is not int or query["limit"] < 0:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}


    matches = []

    for flight in db:
        if "flight_id" in query:
            if flight["flight_id"] != query["flight_id"]:
                continue

        if "origin" in query:
            if flight["origin"] != query["origin"]:
                continue

        if "destination" in query:
            if flight["destination"] != query["destination"]:
                continue

    # Filter by departure datetime
        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                continue

    # Filter by arrival datetime
        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                continue

    # Filter by maximum price
        if "price" in query:
            if flight["price"] > query["price"]:
                continue

    # Filter by minimum price
        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                continue

        matches.append(flight)

    # Sort matching flights
    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=descending
        )

    # Limit the number of results
    if "limit" in query:
        matches = matches[:query["limit"]]


    return {"query": query, "matches": matches}



def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]

