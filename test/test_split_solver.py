import pytest

import split_solver


@pytest.fixture
def A() -> list[int]:
    return [1, 2, 3, 4, 5]


@pytest.fixture
def N() -> int:
    return 3


def test_gen_idxs(A: list[int], N: int) -> None:
    idxs = split_solver.gen_idxs(len(A), N)
    assert len(next(idxs)) == N - 1  # type: ignore


def test_gen_split(A: list[int], N: int) -> None:
    idxs = split_solver.gen_idxs(len(A), N)
    split = split_solver.gen_split(A, next(idxs))  # type: ignore
    assert len(split) == N


def test_find_optimal_split(A: list[int], N: int) -> None:
    optimal_idx = split_solver.find_optimal_split(A, N)
    assert len(optimal_idx) == N - 1


def test_get_optimal_split(A: list[int], N: int) -> None:
    optimal_split = split_solver.get_optimal_split(A, N)
    assert len(optimal_split) == N
