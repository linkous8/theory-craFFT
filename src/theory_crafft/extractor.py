"""Parses the specific table format of a particular FAQ and returns structured
data"""

import re
from decimal import Decimal

import pandas as pd

from . import constants


def extract() -> dict[str, pd.DataFrame] | None:
    """Parses custom formatted table from faq into dataframes.
    Parses Bases and Growths into separate columns"""

    column_headers: pd.Index | None = None

    result: dict[str, pd.DataFrame] = dict()

    current_race: str = ""
    current_race_table: list[pd.Series] = list()

    with open("data/ffta_mechanics_job_stats_only.txt", "r") as input_file:
        for line_num, line in enumerate(input_file):
            # general note that this could be structured with `else if`s but I prefer
            # "return early, return often" strucured flow control using returns/continues
            # with the if statements. This makes the conditions more self
            # contained and makes it harder to introduce bugs when adding new
            # conditions (eg. forgetting to add else before the if)

            if not line:
                continue  # skip empty lines
            if line.startswith("="):
                continue  # skip horizontal rule
            if line.startswith("   Jobs"):
                continue  # skip second header row

            # If row is header, parse column names
            if line.startswith("Player"):
                column_headers = _get_stats_headers(line)
                continue  # finished with this line

            if column_headers is None:
                print(f"Column headers never parsed by line {line_num}")
                return None

            # check for start of new table
            if line.startswith("---"):
                # don't try to add results if we haven't parsed any data yet
                if current_race:
                    # completed a table, add to result
                    result[current_race] = pd.DataFrame(current_race_table)
                    # reset accumultor
                    current_race_table = list()

                # set key/name for new table
                current_race = line.replace("-", "").strip()

                continue  # finished with this line

            job_row = _get_job_stat_values(line, line_num, column_headers)
            if job_row is None:
                continue

            current_race_table.append(job_row)

        # append final race parsed
        if current_race:
            result[current_race] = pd.DataFrame(current_race_table)

    return result


def _get_stats_headers(line: str) -> pd.Index:
    # split line into intial column values
    columns = line.split()[1:]  # slice out first element "Player"

    # is simpler to construct sepearate base and growth columns from
    # this line than to try to parse second line of table
    enhanced_columns = [
        col + post_fix
        for col in columns
        for post_fix in [f" {constants.BASE}", f" {constants.GROWTH}"]
    ]
    return pd.Index(enhanced_columns)


def _get_job_stat_values(
    line: str, line_num: int, COLUMN_HEADERS: pd.Index
) -> pd.Series | None:
    """Get series of stat numbers for job line. Returns none if it cannot be parsed"""

    # Capture letter only words, possibly multiple separated by space
    # (side note, this is an amazing resource for testing regex quickly
    # https://regex101.com/ )
    job_name_match = re.match(r"[a-zA-Z]+(?:\s+(?<=\s)[a-zA-Z]+)*", line)
    if not job_name_match:
        print(f"Warning: could not parse job name for line #{line_num}")
        return None

    # slice job name out
    line = line[job_name_match.end() :]
    # split by slash then by space
    line_values = [
        final_split
        for split_slash in line.split("/")
        for final_split in split_slash.split()
    ]
    if len(line_values) != len(COLUMN_HEADERS):
        print(
            "Warning: number of values parsed did not match expected coutn on "
            "line #{line_num}"
        )

    parsed_values = list(map(Decimal, line_values))
    return pd.Series(parsed_values, index=COLUMN_HEADERS, name=job_name_match.group())
