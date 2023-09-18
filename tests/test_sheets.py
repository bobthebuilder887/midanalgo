from pathlib import Path

from work_divider import sheets


def test_read_table(table_path: Path) -> None:
    table = sheets.read_table(table_path)
    # Check that the shape is as expected
    assert table.shape == (119, 4)


def test_read_tablebase(tablebase_path: Path) -> None:
    tablebase = sheets.read_tablebase(tablebase_path)
    # Check that the shape is as expected
    assert tablebase.shape == (49, 5)
    # Make sure the DEFAULT row is present
    assert "DEFAULT" in tablebase.index


def test_read_names(tablebase_path: Path) -> None:
    names = sheets.read_names(tablebase_path)
    assert len(names) == 11


def test_read_data(table_path: Path, tablebase_path: Path) -> None:
    data = sheets.read_data(table_path, tablebase_path)
    assert len(data) == 3
