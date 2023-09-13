from pathlib import Path

import numpy as np
import pandas as pd

import sheets
import split_solver


def match_invoices(
    batches: dict[int, sheets.Batch], optimal: list[list[int]]
) -> dict[int, list[int]]:
    """Match scores with corresponding invoice numbers"""
    invoice_per_worker = {worker: [] for worker in range(len(optimal))}

    for worker, scores in enumerate(optimal):
        for score in scores:
            batches, invoices = find_matching_invoices(score, batches)
            invoice_per_worker[worker].extend(invoices)

    return invoice_per_worker


def find_matching_invoices(
    score: int,
    batches: dict[int, sheets.Batch],
) -> tuple[dict[int, sheets.Batch], list[int]]:
    for batch_id, batch in batches.copy().items():
        if batch.score == score:
            batches.pop(batch_id)
            return batches, batch.invoice_numbers


def gen_output(
    table: pd.DataFrame,
    matching_invoices: dict[int, list[int]],
) -> pd.DataFrame:
    table["Worker"] = -1
    for worker, invoices in matching_invoices.items():
        table.loc[table["Invoice Number"].isin(invoices), "Worker"] = worker

    table = table[["Worker", "Name", "Invoice Number"]]

    return table


def main() -> None:
    TABLE = Path("test") / "sample_data.xlsx"
    TABLEBASE = Path("test") / "sample_tablebase.xlsx"
    OUTPUT = Path("test") / "output.xlsx"
    N_WORKERS = 3

    table = sheets.read_table(TABLE)
    tablebase = sheets.read_tablebase(TABLEBASE)
    table = table[table["Name"].isin(tablebase.index.values)]  # type: ignore
    batches = sheets.gen_batches(sheets.process_table(table, tablebase))
    scores = sheets.get_scores(batches)

    # TODO: Optimize this step
    optimal = split_solver.get_optimal_split(scores, N_WORKERS)

    expected_avg = np.sum(scores) / N_WORKERS
    optimal_scores = list(np.sum(split) for split in optimal)
    optimal_avg = np.mean(optimal_scores)
    optimal_var = np.var(optimal_scores)

    print(f"Expected AVG: {expected_avg}")
    print(f"Obtained AVG: {optimal_avg}")
    print(f"Obtained VAR: {optimal_var}")
    print(f"Obtained SCORES: {optimal_scores}")

    matching_invoices = match_invoices(batches, optimal)

    output = gen_output(table, matching_invoices)
    output.groupby(["Worker", "Name"])["Invoice Number"].unique().to_excel(OUTPUT)


if __name__ == "__main__":
    main()
