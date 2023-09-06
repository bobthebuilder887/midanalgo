import argparse
from typing import Iterable

import pyexcel
from pyexcel.sheet import Sheet

Row = tuple[str, str, str]


def read_files(table: str, table_base: str) -> tuple[Sheet, Sheet]:
    """Read table and table base files"""

    # Read in relevant columns of main table (assumes first 3 columns are of interest)
    table_sheet = pyexcel.get_sheet(
        file_name=table,
        start_column=0,
        column_limit=3,
        name_columns_by_row=0,
    )

    # Read in base table with row and column names intact
    tablebase = pyexcel.get_sheet(
        file_name=table_base,
        name_columns_by_row=0,
        name_rows_by_column=0,
    )

    return table_sheet, tablebase


def process_table(table_sheet: Sheet) -> Iterable[Row]:
    """
    Convert rows from list to tuple (dictionary key needs to be immutable)
    """
    return (tuple(row) for row in table_sheet)


def process_tablebase(tablebase: Sheet) -> Sheet:
    """
    Rename columns to their corresponding remainder
    """
    n_iter = len(tablebase.colnames)
    tablebase.colnames = list(range(1, n_iter)) + [0]
    return tablebase


def gen_scores(rows: Iterable[Row], tablebase: Sheet) -> list:
    """
    Calculate scores for each table row using tablebase as reference
    """
    scores: list = ["Score"]
    unique_rows: dict[Row, int] = {}
    n_iter = len(tablebase.colnames)

    for row in rows:
        # Count the number of found instances of each row
        if row in unique_rows:
            unique_rows[row] += 1
        else:
            unique_rows[row] = 1
        # Fetch row count
        row_count = unique_rows[row]
        # Get the remainder
        remainder = row_count % n_iter

        # Locate score in the tablebase
        score = tablebase[row[0], remainder]

        # Store score
        scores.append(score)

    return scores


def save_file(scores: list, table_path: str, output_path: str) -> None:
    """add scores to an excel file"""
    # Generate a new sheet with the scores
    new_sheet = pyexcel.get_sheet(file_name=table_path)
    # append scores column to sheet
    new_sheet.column += scores
    # Save as a new file
    new_sheet.save_as(output_path)
    print(f"saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="Midan's Sheet Processor",
        description="Process work table",
        epilog="All files have to be of .xslx type",
    )

    # Table file path
    parser.add_argument(
        "-t",
        "--table",
        help="Path to table file.",
        type=str,
        required=True,
    )
    # Base Table file path
    parser.add_argument(
        "-b",
        "--table-base",
        help="Path to table base file.",
        type=str,
        required=True,
    )
    # Output Table file path
    parser.add_argument(
        "-o",
        "--output-file",
        help="Path to output file.",
        type=str,
        required=True,
    )

    # Parse arguments
    args = parser.parse_args()

    # Read in table and tablebase files
    table_sheet, tablebase = read_files(table=args.table, table_base=args.table_base)

    # get table rows and rename columns of tablebase
    rows, tablebase = process_table(table_sheet), process_tablebase(tablebase)

    # Calculate scores for each table row
    scores = gen_scores(rows, tablebase)

    # Save a new file
    save_file(scores, args.table, args.output_file)


if __name__ == "__main__":
    main()
