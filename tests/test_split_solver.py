import pytest

from work_divider import split_solver


@pytest.fixture
def A() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture
def N() -> int:
    return 3


def test_get_optimal_split(A: list[int], N: int) -> None:
    optimal_split = split_solver.get_optimal_split(A, N)
    assert len(optimal_split) == N
