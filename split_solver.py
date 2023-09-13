import random
from itertools import combinations
from typing import Iterable, Sequence

import numpy as np


def calc_optimal_split(a: Sequence[int], n: int) -> tuple[int, ...]:
    # TODO: order matters for the end result as it is idx based!
    min_var = np.sum(a)
    idxs = gen_idxs(len(a), n)
    optimal_idx = tuple()

    for idx in idxs:
        split = gen_split(a, idx)
        split_var = np.var(split)
        if split_var < min_var:
            optimal_idx = idx
            min_var = split_var

    # TODO: replace with optimal split
    return optimal_idx


def gen_idxs(size: int, n: int) -> Iterable[tuple[int]]:
    return combinations(range(1, size), n - 1)


def gen_split(a: Iterable[int], idxs: tuple[int, ...]) -> list[int]:
    return list(np.sum(frac) for frac in np.split(a, idxs))


def main():
    random.seed(123)
    a = list(range(15))  # TODO: order matters for the end result as it is idx based!
    random.shuffle(a)
    n = 4
    print(a)
    print(np.split(a, calc_optimal_split(a, n)))


if __name__ == "__main__":
    main()
