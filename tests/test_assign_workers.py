import os
from pathlib import Path

import pytest

from work_divider import assign_workers


@pytest.fixture
def table_path() -> Path:
    return Path("tests") / "sample_data.xlsx"


@pytest.fixture
def tablebase_path() -> Path:
    return Path("tests") / "sample_tablebase.xlsx"


def test_main(table_path: Path, tablebase_path: Path) -> None:
    output_path = "tests/output.xlsx"

    assign_workers.main(
        argv=["-t", str(table_path), "-b", str(tablebase_path), "-o", output_path],
    )

    # Test if generates file
    assert Path(output_path).exists()

    os.remove(output_path)
