from pathlib import Path

import pandas as pd
import rich


def read_table(file_path: str | Path) -> pd.DataFrame:
    return pd.read_excel(
        file_path,
        header=11,
        usecols="A:D",
    )


def read_tablebase(file_path: str | Path) -> pd.DataFrame:
    tablebase = pd.read_excel(file_path, header=2, usecols="B:G", index_col=0)

    return tablebase


def process_table(
    table: pd.DataFrame,
    tablebase: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
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

    # Batch identical tasks into groups that don't exceed mod
    batches = dict()
    batch_id = 0
    previous_mod = MOD

    table.columns = list(name.lower().replace(" ", "_") for name in table.columns)

    for row in table.itertuples():
        rich.print(row)
        if row.mod <= previous_mod:
            batch_id += 1
            batches[batch_id] = [0, []]

        batches[batch_id][0] += row.score
        batches[batch_id][1].append(row.invoice_number)

        previous_mod = row.mod
    return table, batches


def main():
    table = read_table("test/sample_data.xlsx")
    tablebase = read_tablebase("test/sample_tablebase.xlsx")
    table, batches = process_table(table, tablebase)
    rich.print(batches)


if __name__ == "__main__":
    main()
