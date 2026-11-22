"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import logging
from pathlib import Path 
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "260AMB071"
FIRST_NAME = "Carmen"
LAST_NAME = "GarciaRosique"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    parser = argparse.ArgumentParser(
        description="Flight schedule parser and query tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i or -d")

    if args.j and args.o:
        parser.error("-o cannot be used with -j")

    try:
        if args.i or args.d:
            if args.i:
                paths = [args.i]
            else:
                folder = Path(args.d)
                paths = sorted(
                    str(p) for p in folder.iterdir()
                    if p.is_file() and p.name.endswith(".csv")
                )

                if not paths:
                    raise ValueError("No CSV files found")

            airports = load_airports(args.a)
            records, errors = parse_files(paths, airports)

            output_path = Path(args.o or "db.json")

            log_path = output_path.parent / "errors.log"

            logger = logging.getLogger("flight_parser")
            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            try:
                for error_message in errors:
                    logger.warning(error_message)
            finally:
                logger.removeHandler(handler)
                handler.close()


            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4)

        else:
            with open(args.j, "r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list) or not all(
                isinstance(record, dict) for record in records
            ):
                raise ValueError("Invalid JSON database")

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, dict) and not (
                isinstance(queries, list)
                and all(isinstance(q, dict) for q in queries)
            ):
                raise ValueError("Invalid query JSON")

            responses = run_queries(records, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = Path(args.r) / response_name

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=4)
   

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0




if __name__ == "__main__":
    sys.exit(main())
