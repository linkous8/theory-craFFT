"""
This module orchestrates the sequencing of utility invocations to write the full
table. Logic is housed here due to main getting too cluttered.
"""

import gspread
from gspread.utils import ValueInputOption
import gspread_formatting
import pandas as pd

from theory_crafft.sheet_writer.format_utils import (
    get_bg_color_format_ranges_for_headers,
    get_bg_color_format_ranges_left_labels,
    get_bold_cell_values_for_dataframe_header,
    get_borders_for_speed_columns,
    get_gradient_rules_for_ehanced_dataframe,
    get_percent_cell_ranges_for_enhanced_dataframe,
)


def write_table_label(
    sheet: gspread.Worksheet, race: str, is_first_section: bool
) -> int:
    """Adds label style header to the sheet. This is not the column headers. It
    is meant to highlight which of the 5 playable races the given section
    corresponds to as well as a divider to more easily tell sections apart

    Args:
        sheet: Target sheed as returned by gspread to which values will be written
        race: Which playable race this label corresponds to
        is_first_row: If we're writing the first section then we can skip the divider

    Returns:
        num_rows_added: The number of rows added to the sheet for incrementing
            row counter tracked externally
    """
    divider_and_race_label = [[race]]
    if not is_first_section:
        divider_and_race_label.insert(0, ["---"])
    sheet.append_rows(divider_and_race_label)
    return len(divider_and_race_label)


def write_race_tables(
    sheet: gspread.Worksheet,
    conditional_formatting_rules: gspread_formatting.ConditionalFormatRules,
    start_index: int,
    base_table: pd.DataFrame,
    growths_table: pd.DataFrame,
) -> int:
    # TODO fix lack of padding in cell widths. Simplest to highlight columns and 
    #      double click a border
    # TODO print stat maximums for each race
    #      add quality of each max stat compared between all races
    # TODO maybe min?
    # TODO batch sheet changes to reduce chances of 429 error
    # TODO left align all values

    rows_added = 0

    # base stats for recruiting
    write_enhanced_dataframe_to_sheet_with_formatting(
        ws=sheet,
        first_col_header="**BASE**",
        df=base_table,
        start_row_index=start_index + rows_added,
        conditional_formatting_rules=conditional_formatting_rules,
    )
    rows_added += len(base_table) + 2  # +2 for divider and header

    # stat growths for training
    write_enhanced_dataframe_to_sheet_with_formatting(
        ws=sheet,
        first_col_header="**GROWTHS**",
        df=growths_table,
        start_row_index=start_index + rows_added,
        conditional_formatting_rules=conditional_formatting_rules,
    )
    rows_added += len(growths_table) + 2  # +2 for divider and header

    return rows_added


def write_enhanced_dataframe_to_sheet_with_formatting(
    ws: gspread.Worksheet,
    first_col_header: str,
    df: pd.DataFrame,
    start_row_index: int,
    conditional_formatting_rules: gspread_formatting.ConditionalFormatRules,
):
    start_index_skip_divider = start_row_index + 1
    ws.append_rows(
        [["---"]]  # header
        + [[first_col_header] + df.columns.tolist()]
        + df.astype(str).reset_index().values.tolist(),
        value_input_option=ValueInputOption.user_entered,
    )

    # make headers bold
    gspread_formatting.format_cell_range(
        worksheet=ws,
        **get_bold_cell_values_for_dataframe_header(
            start_row_index=start_index_skip_divider, df=df
        ),
    )

    # apply color key to headers and left labels
    gspread_formatting.format_cell_ranges(
        worksheet=ws,
        ranges=(
            get_bg_color_format_ranges_for_headers(row_index=start_index_skip_divider)
            + get_bg_color_format_ranges_left_labels(
                row_index=start_index_skip_divider, num_rows=len(df)
            )
        ),
    )

    # percent format
    gspread_formatting.format_cell_ranges(  # type: ignore
        worksheet=ws,
        ranges=get_percent_cell_ranges_for_enhanced_dataframe(
            start_row_index=start_index_skip_divider, df=df
        ),
    )

    # border around speed columns
    gspread_formatting.format_cell_ranges( # type: ignore
        worksheet=ws,
        ranges=get_borders_for_speed_columns(start_index_skip_divider, len(df))
    )

    # Apply color gradient for heatmap
    # rules updated by reference
    conditional_formatting_rules.extend(
        get_gradient_rules_for_ehanced_dataframe(
            start_row_index=start_index_skip_divider,
            sheet_id=ws.id,
            df=df,
        )
    )


# TODO? add_table_format
#   Nvm, throws off the spacing too much
# body = {
#     'requests': [
#         {
#             'addTable': {
#                 'table': {
#                     'name': 'SalesData',
#                     'range': {
#                         'sheetId': 0, # Update with your target Sheet ID
#                         'startRowIndex': 0,
#                         'endRowIndex': 100,
#                         'startColumnIndex': 0,
#                         'endColumnIndex': 4
#                     }
#                 }
#             }
#         }
#     ]
# }
