import random
from pathlib import Path

import pandas as pd

from work_divider import batching, sheets, split_solver
from work_divider.sheet_logs import SHEET_LOG


def match_invoices(
    batches: dict[int, batching.Batch],
    optimal: list[list[int]],
) -> dict[int, list[int]]:
    """Match scores with corresponding invoice numbers"""

    # Initialize a dictionary of workers to store invoice numbers
    invoice_per_worker: dict[int, list[int]] = {i: [] for i in range(len(optimal))}

    # Match invoices using batch scores
    for i, scores in enumerate(optimal):
        for score in scores:
            # Find a invoice batch that matches the score (deletes batch, once found)
            batches, invoices = batching.find_matching_invoices(score, batches)
            # Assign the invoice batch to the worker
            invoice_per_worker[i].extend(invoices)

    return invoice_per_worker


def assign_names(
    matching_invoices: dict[int, list[int]],
    names: list[str],
) -> dict[str, list[int]]:
    """Assign names to invoice batches"""
    return {name: invoices for name, invoices in zip(names, matching_invoices.values())}


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


def save_and_format_to_xlsx(output: pd.Series, output_path: Path) -> None:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        # Convert the dataframe to an XlsxWriter Excel object.
        output.to_excel(writer, sheet_name="Sheet1")
        # Get the xlsxwriter worksheet objects.
        worksheet = writer.sheets["Sheet1"]
        # Automatically set the column width
        worksheet.autofit()


def generate_work_sheet(
    data_path: Path | str,
    tablebase_path: Path | str,
    output_path: Path | str = "output.xlsx",
) -> None:
    # Force Path type for output
    if isinstance(output_path, str):
        output_path = Path(output_path)

    SHEET_LOG.info(f"Generating work sheet for {output_path.absolute()}")

    SHEET_LOG.debug(f"{data_path=}")
    SHEET_LOG.debug(f"{tablebase_path=}")

    try:
        # Read .xlsx data
        table, tablebase, names = sheets.read_data(data_path, tablebase_path)

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

        # Match invoices with work splits (finds a list of invoices for each work score)
        invoices_by_split = match_invoices(batches, optimal)

        # Match invoice lists with worker names
        invoices_by_name = assign_names(invoices_by_split, names)

        # Generate output for the .xlsx report
        output = gen_output(table, invoices_by_name)

        # Save and format the output to an .xlsx file
        save_and_format_to_xlsx(output, output_path)

        # Print a confirmation message
        print(f"File saved to {output_path}")
    except Exception:
        SHEET_LOG.error("Error caught during work sheet generation", exc_info=True)
        raise
