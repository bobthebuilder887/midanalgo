from pathlib import Path

import pytest


@pytest.fixture
def table_path() -> Path:
    return Path("tests") / "sample_data.xlsx"


@pytest.fixture
def tablebase_path() -> Path:
    return Path("tests") / "sample_tablebase.xlsx"


@pytest.fixture
def A() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture
def N() -> int:
    return 3
