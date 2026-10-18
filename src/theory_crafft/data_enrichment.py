"""Once the raw dataframes are extracted, there are a couple of operations that
will improve readability and interpretation of the data"""

from collections.abc import Iterable
from itertools import zip_longest

import pandas as pd

from . import constants


def split_base_and_growths(
    source_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Base stats and stat growths are evaluated for two different purposes.
    Determining the quality of recruits, and determining what job to level a
    character in. There is no benefit to presenting the information for both
    use cases in one place. We present them as separate tables for easier
    reading. A single initial table was only necessary to simplify the logic for
    parsing the source text"""

    base_col_names = _filter_list_containing(source_frame.columns, constants.BASE)
    base_table = source_frame[base_col_names].copy()

    # strip the base/growth qualifier from the column header. Both tables will be presented in
    # the same sheet resulting sheet with growths being at a lower point
    base_table.rename(
        inplace=True,
        columns=_get_params_to_remove_substring_from_name(
            base_col_names,
            f" {constants.BASE}",  # note the space in the string
        ),
    )

    growth_col_names = _filter_list_containing(source_frame.columns, constants.GROWTH)
    growth_table = source_frame[growth_col_names].copy()
    growth_table.rename(
        inplace=True,
        columns=_get_params_to_remove_substring_from_name(
            growth_col_names,
            f" {constants.GROWTH}",  # note the space in the string
        ),
    )

    return (base_table, growth_table)


def _filter_list_containing(input_list: Iterable[str], substring: str) -> list[str]:
    return [val for val in input_list if substring in val]


def _get_params_to_remove_substring_from_name(
    column_names: list[str], to_remove: str
) -> dict[str, str]:
    return {col_name: col_name.replace(to_remove, "") for col_name in column_names}


def enhance_stat_table(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate "quality" values and zip them into the source table"""
    # TODO print stat maximums for each race
    #      add quality of each max stat compared between all races
    #      maybe min and/or average instead?

    df_quality = get_min_max_normalized_table(df)
    merged = pd.concat([df, df_quality], axis=1)

    # zip the columns together so the quality metric for a stat appears next to
    # its actual base/growth values
    reindex_cols = [
        col
        for pair in zip_longest(df.columns, df_quality.columns)
        for col in pair
        if col is not None
    ]
    return merged[reindex_cols]


def get_min_max_normalized_table(df: pd.DataFrame) -> pd.DataFrame:
    # micro optimization - could call these when calculating result below but
    # caching them once is _slightly_ more efficient
    min_columns = df.min()
    max_columns = df.max()
    range_columns = max_columns - min_columns

    result = (df - min_columns) / range_columns
    result["Overall"] = result.mean(axis=1)
    # add some subjective aggregations to help overall comparisons
    result["Bulk"] = result[constants.BULK_COLUMNS].mean(axis=1)
    result["Damage"] = result[constants.DAMAGE_COLUMNS].mean(axis=1)
    result["Front-line"] = result[constants.FRONT_LINE_COLUMNS].mean(axis=1)
    result["Mage"] = result[constants.MAGE_COLUMNS].mean(axis=1)

    # differentiate the columns from the original table
    result = result.add_suffix(f" {constants.QUALITY}")

    # We initially parse floats into big D Decimal to eliminate the chance of
    # binary decimal representation quirks. However, it does not cooperate well
    # with dataframe formatting and the accuracy is less important for displaying
    # these downstream value calculations
    # return result.astype(float)
    return result
