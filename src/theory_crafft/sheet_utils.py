from glob import glob
import json
import os
from dotenv import load_dotenv
import gspread
import gspread_formatting
import sys


def _get_workbook():
    load_dotenv()
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    if not SPREADSHEET_ID:
        raise RuntimeError("Spreadsheet ID missing in .env configuration")

    gs_client = gspread.oauth(
        credentials_filename=glob("client_secret_*.json")[0],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gs_client.open_by_key(SPREADSHEET_ID)


def reset_sheet():

    # uses sheet1 by default
    wb = _get_workbook()
    sheet1 = wb.sheet1
    sheet1.clear()

    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet1.id,
                    "startRowIndex": 0,
                    "endRowIndex": 200,
                    "startColumnIndex": 0,
                    "endColumnIndex": 100,
                },
                "fields": "*",
            }
        }
    ]
    sheet1.spreadsheet.batch_update({"requests": requests})

    # get current rules in order to add more
    rules = gspread_formatting.get_conditional_format_rules(sheet1)
    rules.clear()
    rules.save()


def dump_rules():
    """Print list of conditional formatting rules to console for debug"""
    # uses sheet1 by default
    wb = _get_workbook()
    sheet1 = wb.sheet1

    # get current rules in order to add more
    rules = gspread_formatting.get_conditional_format_rules(sheet1)
    for i, rule in enumerate(rules):  # pyright: ignore[reportUnknownVariableType]
        assert isinstance(rule, gspread_formatting.ConditionalFormatRule)
        print(f"{i}: {json.dumps(rule.to_props(), indent=4)}")


def dump_cell_format():
    if len(sys.argv) != 2:
        print("Usage dump-cell-format A1")
        exit(1)
    cell = sys.argv[1]
    # uses sheet1 by default
    wb = _get_workbook()
    sheet1 = wb.sheet1
    rule = gspread_formatting.get_effective_format(sheet1, cell)
    print(json.dumps(rule.to_props(), indent=4, default=str))
