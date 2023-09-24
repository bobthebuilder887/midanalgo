import random
from pathlib import Path

import pytest

import os
from io import StringIO
from work_divider import divide_work_cli


def test_base_case(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    input = [
        "-t",
        str(table_path),
        "-b",
        str(tablebase_path),
        "-o",
        str(output_path),
    ]

    divide_work_cli.main(argv=input)
    # Test if generates file
    assert Path(output_path).exists()
    # Test if prints correct statement
    assert capsys.readouterr().out == f"File saved to {output_path}\n"


def test_no_output(
    table_path: Path,
    tablebase_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    output_path = "output.xlsx"
    if Path(output_path).exists():
        os.remove(output_path)

    input = [
        "-t",
        str(table_path),
        "-b",
        str(tablebase_path),
    ]

    divide_work_cli.main(argv=input)
    # Test if generates file
    assert Path(output_path).exists()
    # Test if prints correct statement
    assert capsys.readouterr().out == f"File saved to {output_path}\n"
    os.remove(output_path)


def test_existing_file(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    # Make sure file is not present first time
    assert not Path(output_path).exists()

    # monkey patch input to test existing file
    yes_str = StringIO("y\n")
    monkeypatch.setattr("sys.stdin", yes_str)

    input = [
        "-t",
        str(table_path),
        "-b",
        str(tablebase_path),
        "-o",
        str(output_path),
    ]

    # run same input twice
    divide_work_cli.main(argv=input)

    # Test if generates file
    assert Path(output_path).exists()

    divide_work_cli.main(argv=input)

    # Test if generates file
    assert Path(output_path).exists()

    assert capsys.readouterr().out.endswith(f"File saved to {output_path}\n")
