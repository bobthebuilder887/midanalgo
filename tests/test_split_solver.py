from work_divider import split_solver


def test_get_optimal_split(A: list[int], N: int) -> None:
    optimal_split = split_solver.get_optimal_split(A, N)
    # Check if the algorithm split the array in correct number of parts
    assert len(optimal_split) == N
    # Check if the algorithm found the optimal solution
    assert [sum(split) for split in optimal_split] == [5, 5, 5]
