from pathlib import Path

import pandas as pd
from work_divider.sheet_logs import SHEET_LOG


class IncorrectTableFormat(Exception):
    pass


def read_table(file_path: str | Path) -> pd.DataFrame:
    """Read the invoice table"""

    expected_cols = ["Name", "Workqueue", "C_UT_CVG_Attention"]

    if isinstance(file_path, str):
        file_path = Path(file_path)

    file = pd.read_excel(
        file_path,
        header=11,
        usecols="A:D",
    )

    if any(col not in file.columns for col in expected_cols):
        raise IncorrectTableFormat(
            f"Column(s): {expected_cols} not found in {file_path}. Please specifiy a valid table!"
        )

    return file


def read_tablebase(file_path: str | Path) -> pd.DataFrame:
    """Read the tablebase table"""

    if isinstance(file_path, str):
        file_path = Path(file_path)

    DEFAULT_SCORES = 12, 6, 4, 4, 2

    tablebase = pd.read_excel(file_path, header=2, usecols="B:G", index_col=0)

    if tablebase.index.name != "Payor Name":
        raise IncorrectTableFormat(
            f"Index name not 'Payor Name' in {file_path}. Please specify a valid tablebase!"
        )

    # Make sure column names are just their number
    tablebase.columns = list(range(tablebase.shape[1]))

    # Make sure there exists a DEFAULT row
    if "DEFAULT" not in tablebase.index:
        tablebase.loc["DEFAULT", :] = DEFAULT_SCORES  # type: ignore
        SHEET_LOG.warning(f"Added DEFAULT row {DEFAULT_SCORES=} to tablebase")

    return tablebase


def read_names(file_path: str | Path, sheet_name="Workers") -> list[str]:
    """Read the worker names"""

    if isinstance(file_path, str):
        file_path = Path(file_path)

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except ValueError:
        raise IncorrectTableFormat(
            f"Sheet '{sheet_name}' not found in {file_path}! Please specify a valid tablebase!"
        )

    return list(df["Agent"].values)


def read_data(
    table_path: Path | str,
    tablebase_path: Path | str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Read all required data from files"""
    table = read_table(table_path)
    names = read_names(tablebase_path)
    tablebase = read_tablebase(tablebase_path)
    return table, tablebase, names
