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


def test_existing_file_yes(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    # Make sure file is not present first time
    assert not Path(output_path).exists()

    # monkey patch input to test existing file with a yes
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

    # Save creation time
    ctime1 = os.path.getmtime(output_path)

    divide_work_cli.main(argv=input)

    # Save creation time
    ctime2 = os.path.getmtime(output_path)

    # Test if generates file
    assert Path(output_path).exists()

    # Test if prints correct statement
    assert capsys.readouterr().out.endswith(f"File saved to {output_path}\n")

    # Test if file has been overwritten
    assert ctime1 != ctime2


def test_existing_file_no(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    # Make sure file is not present first time
    assert not Path(output_path).exists()

    # monkey patch input to test existing file with a yes
    yes_str = StringIO("n\n")
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

    # Test if generates file the first time
    assert Path(output_path).exists()

    ctime1 = os.path.getmtime(output_path)

    divide_work_cli.main(argv=input)

    ctime2 = os.path.getmtime(output_path)

    # Test if terminates at (y/n) prompt
    assert capsys.readouterr().out.endswith("Do you want to overwrite it? (y/n)\n")

    # Test if output file has not been overwritten
    assert ctime1 == ctime2
