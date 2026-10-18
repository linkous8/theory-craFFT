from dotenv import load_dotenv
from glob import glob
import gspread
import gspread_formatting
import os

from theory_crafft.sheet_writer.writer import write_race_tables, write_table_label

from .extractor import extract
from .data_enrichment import split_base_and_growths, enhance_stat_table


def main():
    # load user specified configuration
    load_dotenv()

    # The ID and range of a sample spreadsheet.
    # TODO accept a spreadsheet title
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    if not SPREADSHEET_ID:
        raise RuntimeError("Spreadsheet ID missing in .env configuration")

    gs_client = gspread.oauth(
        credentials_filename=glob("client_secret_*.json")[0],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    wb = gs_client.open_by_key(SPREADSHEET_ID)

    # uses sheet1 by default
    sheet1 = wb.sheet1

    # get current rules in order to add more
    rules = gspread_formatting.get_conditional_format_rules(sheet1)

    # Extract datafram by parsing text based table from gamefaq
    raw_table = extract()
    if raw_table is None:
        raise RuntimeError("No data partsed from sheet")

    cur_row_index = 0
    num_columns_to_resize = 0
    for race, raw_data_df in raw_table.items():
        # start new section
        cur_row_index += write_table_label(sheet1, race, cur_row_index == 0)

        # original file formatted as "base/growth" per cell. Split into two tables
        base_df, growth_df = split_base_and_growths(raw_data_df)

        # enhance tables with min-max normalized percent columns
        enhanced_base = enhance_stat_table(base_df)
        enhanced_growths = enhance_stat_table(growth_df)

        cur_row_index += write_race_tables(
            sheet=sheet1,
            conditional_formatting_rules=rules,
            start_index=cur_row_index,
            base_table=enhanced_base,
            growths_table=enhanced_growths,
        )

        # all tables are same width but this calculation supports potential future
        # heterogenity
        num_columns_to_resize = max(
            num_columns_to_resize,
            len(enhanced_base.columns) + 1,
            len(enhanced_growths.columns) + 1,
        )

        # FIXME DELETE ME
        # rules.save()
        # return

    # apply changes to rules updated by reference
    rules.save()

    # FIXME the cells still seem squished and requires a manual resize
    sheet1.columns_auto_resize(0, num_columns_to_resize)
    return


if __name__ == "__main__":
    main()
