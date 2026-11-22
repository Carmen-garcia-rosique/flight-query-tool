"""Reading CSV files into flight records and error messages."""
import csv
from pathlib import Path

from validator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []

    seen_flights = set()

    for path in paths:
        with open(path, "r", encoding="utf-8", newline="") as file:
            next(file)

            for line_number, line in enumerate(file, start=2):
                stripped_line = line.strip()

                if not stripped_line:
                    continue

                if stripped_line.startswith("#"):
                    continue

                fields = next(csv.reader([line]))
                error = validate_row(fields, airports)

                if error is None:
                    record = to_record(fields)

                    flight_key = (
                        record["flight_id"],
                        record["departure_datetime"]
                    )

                    if flight_key in seen_flights:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen_flights.add(flight_key)
                        records.append(record)

                if error is not None:
                    message = f"{Path(path).name}:{line_number}: {error} | {stripped_line}"
                    errors.append(message)


    return records, errors
