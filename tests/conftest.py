import os
from pathlib import Path

import pytest
from work_divider.sheet_logs import SHEET_LOG


@pytest.fixture
def table_path() -> Path:
    return Path("tests") / "sample_data.xlsx"


@pytest.fixture
def tablebase_path() -> Path:
    return Path("tests") / "sample_tablebase.xlsx"


@pytest.fixture
def output_path() -> Path:
    return Path("tests") / "output.xlsx"


@pytest.fixture
def A() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture
def N() -> int:
    return 3


@pytest.fixture
def log_path() -> Path:
    return Path(SHEET_LOG.handlers[0].baseFilename)  # type: ignore


@pytest.fixture(autouse=True)
def clean_dir(output_path: Path, log_path: Path):
    yield
    if output_path.exists():
        os.remove(output_path)

    if log_path.exists():
        SHEET_LOG.propagate = False
        os.remove(log_path)
        # SHET_LOG.propagate = True
