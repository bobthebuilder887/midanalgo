from itertools import combinations
from typing import Iterable, Sequence

import numpy as np


def get_optimal_split(a: Sequence[int], n: int) -> list:
    """
    Get split indices that give the smallest variance between splits the given an array
    and number of splits
    """
    return np.split(a, find_optimal_split(a, n))


def find_optimal_split(a: Sequence[int], n: int) -> tuple[int, ...]:
    """
    Find split indices that give the smallest variance between splits the given an array
    and number of splits
    """

    # Initalize variables
    min_var = np.sum(a)
    idxs = gen_idxs(len(a), n)
    optimal_idx = tuple()

    for idx in idxs:
        split = gen_split(a, idx)  # generate split with summed scores
        split_var = np.var(split)  # calculate variance
        if split_var < min_var:  # replace if variance smaller than minimum found
            optimal_idx = idx
            min_var = split_var

    return optimal_idx


def gen_idxs(size: int, n: int) -> Iterable[tuple[int]]:
    """Generate all possible split indices given a size and number of splits"""
    return combinations(range(1, size), n - 1)


def gen_split(a: Iterable[int], idxs: tuple[int, ...]) -> list[int]:
    """Generate splits with summed scores"""
    return list(np.sum(frac) for frac in np.split(a, idxs))  # type: ignore
