from dataclasses import dataclass, field

import pandas as pd
from work_divider.sheet_logs import SHEET_LOG


def process_table(table: pd.DataFrame, tablebase: pd.DataFrame) -> pd.DataFrame:
    """Add a matching score to each invoice row and pre-format for invoce batching"""

    group_cols = ["Name", "Workqueue", "C_UT_CVG_Attention"]

    # Sort by task columns
    table = table.sort_values(by=group_cols)

    # Add a counter for each unique task
    table["Count"] = 1
    table["Count"] = table.groupby(group_cols)["Count"].cumsum()

    # Change the columns to modulo of the number of columns
    MOD = tablebase.shape[1]
    tablebase.columns = list(range(1, MOD)) + [0]

    # Add a modulo column to find the reference score
    table["Mod"] = table["Count"].mod(MOD)

    missing_names: set[str] = set()

    def find_score(row: pd.Series, tablebase: pd.DataFrame) -> int:
        if row["Name"] in tablebase.index:
            return tablebase.loc[row["Name"], row["Mod"]]  # type: ignore
        else:
            # If missing add to a set for log message
            missing_names.add(row["Name"])  # type: ignore
            return tablebase.loc["DEFAULT", row["Mod"]]  # type: ignore

    # Add task score
    table["Score"] = table.apply(find_score, axis=1, tablebase=tablebase)

    # Log message for missing name scores
    if missing_names:
        msgs = []
        msgs.append("Following names using DEFAULT row from tablebase: ")
        for name in missing_names:
            score_values = table.loc[table["Name"] == name, "Score"].values
            score_values = ", ".join([str(int(score)) for score in score_values])
            msgs.append(f"\t- {name} (added score(s): {score_values})")
        SHEET_LOG.warning("\n".join(msgs))

    # Change from modulo to the ocurrence number in the table
    # i.e. if it is 5 items in a row max then 1, 2, 3, 4, 0 becomes 0, 1, 2, 3, 4
    # This makes for simpler batch generation (see gen batches)
    table["Mod"] = table["Mod"].replace(dict(zip(tablebase.columns, range(MOD))))

    # Rename and filter columns so it is easier to work with
    table.columns = list(name.lower().replace(" ", "_") for name in table.columns)
    table = table[["mod", "score", "invoice_number"]]  # type: ignore

    return table


_ID = -1


def _gen_id() -> int:
    """Helper function to assign unique IDs to batches"""
    global _ID
    _ID += 1
    return _ID


@dataclass
class Batch:
    id: int = field(default_factory=_gen_id)
    score: int = field(default=0)
    invoice_numbers: list = field(default_factory=list)

    def add_invoice(self, invoice_number: int, score: int) -> None:
        self.invoice_numbers.append(invoice_number)
        self.score += score


def gen_batches(table: pd.DataFrame) -> dict[int, Batch]:
    """
    Batch identical tasks into groups that don't exceed the size of mod

    Assumes table is sorted by the type of task!
    """

    batches, batch, previous_mod = {}, Batch(), -1
    batches[batch.id] = batch

    @dataclass
    class Row:
        mod: int
        score: int
        invoice_number: int

    for row in (Row(**row) for _, row in table.iterrows()):  # type: ignore
        if row.mod <= previous_mod:
            batch = Batch()
            batches[batch.id] = batch

        batches[batch.id].add_invoice(
            score=row.score,
            invoice_number=row.invoice_number,
        )

        previous_mod = row.mod

    return batches


def get_scores(batches: dict[int, Batch]) -> list[int]:
    """Get the score for each batch"""
    return [batch.score for batch in batches.values()]


def find_matching_invoices(
    score: int,
    batches: dict[int, Batch],
) -> tuple[dict[int, Batch], list[int]]:
    """Find a batch of invoices that matches the score"""

    for batch_id, batch in batches.copy().items():
        if batch.score == score:
            batches.pop(batch_id)
            return batches, batch.invoice_numbers  # type: ignore

    raise ValueError("No matching batch found")
