from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


def read_table(file_path: str | Path) -> pd.DataFrame:
    """Read the invoice table"""
    return pd.read_excel(
        file_path,
        header=11,
        usecols="A:D",
    )


def read_tablebase(file_path: str | Path) -> pd.DataFrame:
    """Read the tablebase table"""
    tablebase = pd.read_excel(file_path, header=2, usecols="B:G", index_col=0)
    return tablebase


def process_table(table: pd.DataFrame, tablebase: pd.DataFrame) -> pd.DataFrame:
    """Add a matching score to each invoice row"""

    # TODO: review with Midan
    # Remove tasks that don't have a score reference
    table = table[table["Name"].isin(tablebase.index.values)]  # type: ignore

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
    # Add task score

    def find_score(row: pd.Series, tablebase: pd.DataFrame) -> int:
        return tablebase.loc[row["Name"], row["Mod"]]

    table["Score"] = table.apply(find_score, axis=1, tablebase=tablebase)
    table["Mod"] = table["Mod"].replace(dict(zip(tablebase.columns, range(MOD))))

    return table


_ID = -1


def _gen_id() -> int:
    global _ID
    _ID += 1
    return _ID


@dataclass
class Batch:
    id: int = field(default_factory=_gen_id)
    score: int = field(default=0)
    invoice_numbers: list = field(default_factory=list)

    def add_invoice_number(self, invoice_number: int) -> None:
        self.invoice_numbers.append(invoice_number)

    def add_score(self, score: int) -> None:
        self.score += score


def gen_batches(table: pd.DataFrame) -> dict[int, Batch]:
    """
    Batch identical tasks into groups that don't exceed the size of mod

    Assumes table is sorted by the type of task!
    """

    batches, batch, previous_mod = {}, Batch(), -1
    batches[batch.id] = batch

    # Rename and filter columns so it is easier to work with
    table.columns = list(name.lower().replace(" ", "_") for name in table.columns)
    table = table[["mod", "score", "invoice_number"]]

    @dataclass
    class Row:
        mod: int
        score: int
        invoice_number: int

    for row in (Row(**row) for _, row in table.iterrows()):  # type: ignore
        if row.mod <= previous_mod:
            batch = Batch()
            batches[batch.id] = batch

        batches[batch.id].add_score(row.score)
        batches[batch.id].add_invoice_number(row.invoice_number)

        previous_mod = row.mod

    return batches


def get_scores(batches: dict[int, Batch]) -> list[int]:
    """Get the score for each batch"""
    return [batch.score for batch in batches.values()]
