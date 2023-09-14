import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd

import sheets
import split_solver


def match_invoices(
    batches: dict[int, sheets.Batch], optimal: list[list[int]], names: list[str]
) -> dict[str, list[int]]:
    """Match scores with corresponding invoice numbers"""

    # Randomly assign name to each batch of invoices
    random.shuffle(names)

    # Initialize a dictionary of workers to store invoice numbers
    invoice_per_worker = {name: [] for name in names}

    # Match invoices using batch scores
    for name, scores in zip(names, optimal):
        for score in scores:
            batches, invoices = find_matching_invoices(score, batches)
            invoice_per_worker[name].extend(invoices)

    return invoice_per_worker


def find_matching_invoices(
    score: int,
    batches: dict[int, sheets.Batch],
) -> tuple[dict[int, sheets.Batch], list[int]]:
    for batch_id, batch in batches.copy().items():
        if batch.score == score:
            batches.pop(batch_id)
            return batches, batch.invoice_numbers
    return batches, []


def gen_output(
    table: pd.DataFrame,
    matching_invoices: dict[str, list[int]],
) -> pd.Series:
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


def save_output(output: pd.Series, path: str | Path) -> None:
    output.to_excel(path)


def main() -> None:
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
        default="output.xlsx",
        required=False,
    )

    # Parse arguments
    args = parser.parse_args()

    table = sheets.read_table(args.table)

    tablebase = sheets.read_tablebase(args.table_base)
    names = sheets.read_names(args.table_base)

    n_workers = len(names)

    batches = sheets.gen_batches(sheets.process_table(table, tablebase))
    scores = sheets.get_scores(batches)

    # TODO: Optimize this step
    optimal = split_solver.get_optimal_split(scores, n_workers)

    expected_avg = np.sum(scores) / n_workers
    optimal_scores = list(np.sum(split) for split in optimal)
    optimal_avg = np.mean(optimal_scores)
    optimal_var = np.var(optimal_scores)

    print(f"Obtained AVG: {optimal_avg}")
    print(f"Obtained VAR: {optimal_var}")
    print(f"Obtained SCORES: {optimal_scores}")

    matching_invoices = match_invoices(batches, optimal, names)

    # Generate output for the output
    output = gen_output(table, matching_invoices)

    # Save to a specified excel file
    save_output(output, args.output_file)


if __name__ == "__main__":
    main()
