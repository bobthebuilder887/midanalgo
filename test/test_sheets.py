from pathlib import Path

import sheets

TABLE = Path("test") / "sample_data.xlsx"
TABLEBASE = Path("test") / "sample_tablebase.xlsx"


def test_reads_table() -> None:
    expected_shape = (119, 4)
    table = sheets.read_table(TABLE)
    # Check that the shape is as expected
    assert table.shape == expected_shape


def test_read_tablebase() -> None:
    expected_shape = (48, 5)
    tablebase = sheets.read_tablebase(TABLEBASE)
    # Check that the shape is as expected
    assert tablebase.shape == expected_shape


def test_process_table() -> None:
    table = sheets.read_table(TABLE)
    tablebase = sheets.read_tablebase(TABLEBASE)
    table = sheets.process_table(table, tablebase)
    # Check that Score column is generated
    assert "Score" in table.columns


def test_gen_batches() -> None:
    table = sheets.read_table(TABLE)
    tablebase = sheets.read_tablebase(TABLEBASE)
    MOD = tablebase.shape[1]
    batches = sheets.gen_batches(sheets.process_table(table, tablebase))

    # batch score is always greater than 0
    assert (batch.score > 0 for batch in batches.values())
    # Number of invoices doesn't exceed MOD
    assert (len(batch.invoice_numbers) <= MOD for batch in batches.values())


def test_get_scores() -> None:
    table = sheets.read_table(TABLE)
    tablebase = sheets.read_tablebase(TABLEBASE)
    batches = sheets.gen_batches(sheets.process_table(table, tablebase))
    scores = sheets.get_scores(batches)
    # Check that number of scores matches the number of batches
    assert len(scores) == len(batches)
