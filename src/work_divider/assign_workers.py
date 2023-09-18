import argparse
import random
from pathlib import Path
from typing import Sequence

import pandas as pd

from work_divider import batching, sheets, split_solver


def match_invoices(
    batches: dict[int, batching.Batch],
    optimal: list[list[int]],
) -> dict[int, list[int]]:
    """Match scores with corresponding invoice numbers"""

    # Initialize a dictionary of workers to store invoice numbers
    invoice_per_worker = {i: [] for i in range(len(optimal))}

    # Match invoices using batch scores
    for i, scores in invoice_per_worker.items():
        for score in scores:
            # Find a invoice batch that matches the score (deletes batch, once found)
            batches, invoices = batching.find_matching_invoices(score, batches)
            # Assign the invoice batch to the worker
            invoice_per_worker[i].extend(invoices)

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


def assign_names(
    matching_invoices: dict[int, list[int]],
    names: list[str],
) -> dict[str, list[int]]:
    return {name: invoices for name, invoices in zip(names, matching_invoices.values())}


def gen_work_division_table(
    names: list[str],
    table: pd.DataFrame,
    tablebase: pd.DataFrame,
) -> pd.Series:
    # Get number of workers
    n_workers = len(names)

    # Randomize name order for random name assignment
    random.shuffle(names)

    # Assign work score to each invoice and batch by type
    batches = batching.gen_batches(batching.process_table(table, tablebase))

    # Get batch scores
    scores = batching.get_scores(batches)

    # Find the optimal work split
    optimal = split_solver.get_optimal_split(scores, n_workers)

    # Match invoices with work splits
    matching_invoices = match_invoices(batches, optimal)

    # Assign names
    matching_invoices = assign_names(matching_invoices, names)

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
    table, tablebase, names = sheets.read_data(data_path, tablebase_path)
    output = gen_work_division_table(names, table, tablebase)
    # Save to a specified excel file
    save_output(output, output_path)
    print(f"File saved to {output_path}")


def main(argv: Sequence[str] | None = None) -> None:
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
