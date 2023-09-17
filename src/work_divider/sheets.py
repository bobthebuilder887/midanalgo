import logging
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

    DEFAULT_SCORES = 12, 6, 4, 4, 2

    tablebase = pd.read_excel(file_path, header=2, usecols="B:G", index_col=0)

    if "DEFAULT" not in tablebase.index:
        tablebase.loc["DEFAULT", :] = DEFAULT_SCORES
        logging.warning(f"Added DEFAULT row {DEFAULT_SCORES=} to tablebase")

    return tablebase


def read_names(file_path: str | Path, sheet_name="Workers") -> list[str]:
    """Read the worker names"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return list(df["Agent"].values)
