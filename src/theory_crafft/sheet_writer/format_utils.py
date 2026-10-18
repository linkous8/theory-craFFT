from typing import TypedDict
import pandas as pd
from gspread.utils import rowcol_to_a1
from gspread_formatting import (
    Border,
    Borders,
    CellFormat,
    Color,
    ColorStyle,
    ConditionalFormatRule,
    GradientRule,
    GridRange,
    InterpolationPoint,
    TextFormat,
)

# import theory_crafft.colors as colors
from theory_crafft.sheet_writer import colors
from theory_crafft.constants import (
    NUM_QUALITATIVE_COLUMNS,
    NUM_SPEED_COLUMNS,
    NUM_STAT_COLUMNS_NO_SPEED,
    QUALITY,
)

### Percent formatting handlers

PERCENT_FORMAT = CellFormat(numberFormat={"type": "PERCENT", "pattern": "0%"})
BOLD_FORMAT = CellFormat(textFormat=TextFormat(bold=True))


class FormatCellRangeArgs(TypedDict):
    name: str
    cell_format: CellFormat


def get_bold_cell_values_for_dataframe_header(
    start_row_index: int, df: pd.DataFrame
) -> FormatCellRangeArgs:
    """Format headers as bold text"""
    # rowcol_to_a1 takes 1 indexed inputs
    header_start_cell = rowcol_to_a1(start_row_index + 1, 1)
    header_end_cell = rowcol_to_a1(start_row_index + 1, len(df.columns) + 2)
    return {
        "name": f"{header_start_cell}:{header_end_cell}",
        "cell_format": BOLD_FORMAT,
    }


def get_percent_cell_ranges_for_enhanced_dataframe(
    start_row_index: int, df: pd.DataFrame
):
    """Format relevant columns as integer percents. Handle translation from 0
    based index to A1 formatting. Assumes percent column headers contain the
    text of the QUALITY connstant"""

    # skip table headers
    start_data_index = start_row_index + 1

    quality_column_indexes = [
        index + 1  # pandas does not consider row labels (index) to be a column
        for index, column in enumerate(df.columns)
        if QUALITY in column
    ]
    # Note rowcol_to_a1 uses 1 based indexing
    return [
        (
            # note this is a single string, multi-line for readability
            (
                f"{rowcol_to_a1(start_data_index + 1, col_index + 1)}"
                f":{rowcol_to_a1(start_data_index + len(df), col_index + 1)}"
            ),
            PERCENT_FORMAT,
        )
        for col_index in quality_column_indexes
    ]


### Conditional formatting handlers

GRADIENT_RULE = GradientRule(
    minpoint=InterpolationPoint(colorStyle=ColorStyle(rgbColor=colors.RED), type="MIN"),
    midpoint=InterpolationPoint(
        colorStyle=ColorStyle(rgbColor=colors.WHITE), type="PERCENT", value="50"
    ),
    maxpoint=InterpolationPoint(
        colorStyle=ColorStyle(rgbColor=colors.GREEN), type="MAX"
    ),
)


def get_gradient_rule_for_range(
    sheet_id: int,
    start_row_index: int,
    end_row_index: int,
    start_col_index: int,
    end_col_index: int,
):
    """Returns our cookie cutter conditional formatting rule based on one of the
    gradient options available in the sheets UI. Taks care of 0 to 1 index
    conversion as well
    """

    return ConditionalFormatRule(
        ranges=[
            GridRange(
                sheetId=sheet_id,
                startRowIndex=start_row_index + 1,  # skip table headers
                endRowIndex=end_row_index,
                startColumnIndex=start_col_index,
                endColumnIndex=end_col_index,
            )
        ],
        gradientRule=GRADIENT_RULE,
    )


def get_gradient_rules_for_ehanced_dataframe(
    start_row_index: int, sheet_id: int, df: pd.DataFrame
):
    """Gets a list of Conditional Formatting rules for the dataframe. Assumes
    dataframe will be occupying the first column available in the dataframe,
    skips first column assuming it to be headers. Assumes all columns contain
    numbers that make sense in a gradient (in other words, our enhanced dataframe)"""

    # note sheets excludes the ends of ranges
    return [
        get_gradient_rule_for_range(
            sheet_id=sheet_id,
            start_row_index=start_row_index,
            end_row_index=start_row_index + len(df) + 1,
            start_col_index=col_index,
            end_col_index=col_index + 1,
        )
        for col_index in range(1, len(df.columns) + 1)
    ]


def get_bg_color_format_ranges_for_headers(row_index: int):
    # avoids verbose additions in rowcol_to_a1 args
    a1_row = row_index + 1
    current_column = 2

    range_start = rowcol_to_a1(row=a1_row, col=current_column)
    current_column += NUM_STAT_COLUMNS_NO_SPEED - 1
    range_end = rowcol_to_a1(row=a1_row, col=current_column)
    stat_headers_non_speed = f"{range_start}:{range_end}"

    current_column += 1
    range_start = rowcol_to_a1(row=a1_row, col=current_column)
    current_column += NUM_SPEED_COLUMNS - 1
    range_end = rowcol_to_a1(row=a1_row, col=current_column)
    speed_stat_headers = f"{range_start}:{range_end}"

    current_column += 1
    range_start = rowcol_to_a1(row=a1_row, col=current_column)
    current_column += NUM_QUALITATIVE_COLUMNS - 1
    range_end = rowcol_to_a1(row=a1_row, col=current_column)
    qualitative_headers = f"{range_start}:{range_end}"

    return [
        (
            stat_headers_non_speed,
            CellFormat(backgroundColorStyle=ColorStyle(rgbColor=colors.LIGHT_INDIGO)),
        ),
        (
            speed_stat_headers,
            CellFormat(backgroundColorStyle=ColorStyle(rgbColor=colors.LIGHT_YELLOW)),
        ),
        (
            qualitative_headers,
            CellFormat(backgroundColorStyle=ColorStyle(rgbColor=colors.LIGHT_BLUE)),
        ),
    ]


def get_bg_color_format_ranges_left_labels(row_index: int, num_rows: int):
    start_row = row_index + 2
    range_start = rowcol_to_a1(row=start_row, col=1)
    end_row = row_index + 1 + num_rows
    range_end = rowcol_to_a1(row=end_row, col=1)
    return [
        (
            f"{range_start}:{range_end}",
            CellFormat(backgroundColorStyle=ColorStyle(rgbColor=colors.BLUE)),
        )
    ]


# TODO standard stat boarders INDIGO


def get_outer_border_format(
    color: Color,
    row_index_start: int,
    row_index_end: int,
    col_index_start: int,
    col_index_end: int,
) -> list[tuple[str, CellFormat]]:
    """Get format object that applies a thick outer border of a given color to 0 
    based index box of cells"""
    border_format = Border(style="SOLID_THICK", colorStyle=ColorStyle(rgbColor=color))

    # corner borders
    top_left = (
        rowcol_to_a1(row_index_start + 1, col_index_start + 1),
        CellFormat(borders=Borders(top=border_format, left=border_format))
    )
    top_right = (
        rowcol_to_a1(row_index_start + 1, col_index_end + 1),
        CellFormat(borders=Borders(top=border_format, right=border_format))
    )
    bottom_left = (
        rowcol_to_a1(row_index_end + 1, col_index_start + 1),
        CellFormat(borders=Borders(bottom=border_format, left=border_format))
    )
    bottom_right = (
        rowcol_to_a1(row_index_end + 1, col_index_end + 1),
        CellFormat(borders=Borders(bottom=border_format, right=border_format))
    )

    # top+bottom sides
    sides: list[tuple[str, CellFormat]] = []
    if col_index_end - col_index_start > 1:
        # top side
        sides.append((
            f"{rowcol_to_a1(row_index_start + 1, col_index_start + 2)}:{rowcol_to_a1(row_index_start + 1, col_index_end)}",
            CellFormat(borders=Borders(top=border_format))
        ))
        # bottom side
        sides.append((
            f"{rowcol_to_a1(row_index_end + 1, col_index_start + 2)}:{rowcol_to_a1(row_index_end + 1, col_index_end)}",
            CellFormat(borders=Borders(bottom=border_format))
        ))

    # left+right sides
    if row_index_end - row_index_start > 1:
        # left side
        sides.append((
            f"{rowcol_to_a1(row_index_start + 2, col_index_start + 1)}:{rowcol_to_a1(row_index_end, col_index_start + 1)}",
            CellFormat(borders=Borders(left=border_format))
        ))
        # right side
        sides.append((
            f"{rowcol_to_a1(row_index_start + 2, col_index_end + 1)}:{rowcol_to_a1(row_index_end, col_index_end + 1)}",
            CellFormat(borders=Borders(right=border_format))
        ))

    return [
        top_left,
        top_right,
        bottom_left,
        bottom_right,
        *sides
    ]

def get_borders_for_speed_columns(row_index: int, num_rows: int):
    start_col_index = 1 # skip left header
    start_col_index += NUM_STAT_COLUMNS_NO_SPEED
    end_col_index = start_col_index + NUM_SPEED_COLUMNS - 1

    return get_outer_border_format(
        colors.ABSOLUTE_RED,
        row_index,
        row_index + num_rows,
        start_col_index,
        end_col_index
    )
