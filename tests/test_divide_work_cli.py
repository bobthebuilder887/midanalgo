import random
from pathlib import Path

import pytest

from work_divider import divide_work_cli


def test_main(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    random.seed(123)  # Seed for consistent output

    divide_work_cli.main(
        argv=[
            "-t",
            str(table_path),
            "-b",
            str(tablebase_path),
            "-o",
            str(output_path),
        ],
    )

    # Test if generates file
    assert Path(output_path).exists()

    # Test if prints correct statement
    assert capsys.readouterr().out == f"File saved to {output_path}\n"
