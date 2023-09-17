import argparse
import random
from pathlib import Path

import pandas as pd

import sheets
import split_solver


def read_data(
    table_path: Path | str,
    tablebase_path: Path | str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Read all required data from files"""
    table = sheets.read_table(table_path)
    tablebase = sheets.read_tablebase(tablebase_path)
    names = sheets.read_names(tablebase_path)
    return table, tablebase, names


def find_matching_invoices(
    score: int,
    batches: dict[int, sheets.Batch],
) -> tuple[dict[int, sheets.Batch], list[int]]:
    """Find a batch of invoices that matches the score"""
    for batch_id, batch in batches.copy().items():
        if batch.score == score:
            batches.pop(batch_id)
            return batches, batch.invoice_numbers
    return batches, []


def match_invoices(
    batches: dict[int, sheets.Batch], optimal: list[list[int]], names: list[str]
) -> dict[str, list[int]]:
    """Match scores with corresponding invoice numbers and assign a random name"""

    # Randomly assign name to each batch of invoices
    random.shuffle(names)

    # Initialize a dictionary of workers to store invoice numbers
    invoice_per_worker = {name: [] for name in names}

    # Match invoices using batch scores
    for name, scores in zip(names, optimal):
        for score in scores:
            # Find a invoice batch that matches the score (deletes batch, once found)
            batches, invoices = find_matching_invoices(score, batches)
            # Assign the invoice batch to the worker
            invoice_per_worker[name].extend(invoices)

    return invoice_per_worker


def gen_output(
    table: pd.DataFrame,
    matching_invoices: dict[str, list[int]],
) -> pd.Series:
    """Generate the output for the .xlsx file"""
    # Add workers to the original table
    table["Worker"] = ""
    for worker, invoices in matching_invoices.items():
        table.loc[table["Invoice Number"].isin(invoices), "Worker"] = worker

    # Group invoice numbers by worker and type
    output = table.groupby(
        [
            "Worker",
            "Name",
            "C_UT_CVG_Attention",
        ]
    )["Invoice Number"].unique()

    return output


def gen_work_division_table(
    names: list[str],
    table: pd.DataFrame,
    tablebase: pd.DataFrame,
) -> pd.Series:
    # Get number of workers
    n_workers = len(names)

    # Assign work score to each invoice and batch by type
    batches = sheets.gen_batches(sheets.process_table(table, tablebase))
    # Get batch scores
    scores = sheets.get_scores(batches)

    # Find the optimal work split
    optimal = split_solver.get_optimal_split(scores, n_workers)

    # Match invoices with work splits
    matching_invoices = match_invoices(batches, optimal, names)

    # Generate output for the .xlsx report
    return gen_output(table, matching_invoices)


def save_output(output: pd.Series, path: str | Path) -> None:
    output.to_excel(path)


def generate_work_sheet(
    data_path: Path | str,
    tablebase_path: Path | str,
    output_path: Path | str = "output.xlsx",
) -> None:
    """Divide invoces among workers evenly and generate an excel sheet"""
    table, tablebase, names = read_data(data_path, tablebase_path)
    output = gen_work_division_table(names, table, tablebase)
    # Save to a specified excel file
    save_output(output, output_path)
    print(f"File saved to {output_path}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="Midan's Sheet Processor",
        description="Process work table",
        epilog="All files have to be of .xlsx type",
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
        default="output.xlsx",
        required=False,
    )

    # Parse arguments
    args = parser.parse_args(argv)

    generate_work_sheet(args.table, args.table_base, args.output_file)


if __name__ == "__main__":
    main()
