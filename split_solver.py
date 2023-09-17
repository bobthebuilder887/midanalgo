from numberpartitioning import karmarkar_karp


def get_optimal_split(a: list[int], n: int) -> list[list[int]]:
    """
    Get split indices that give the smallest difference of sums between splits the given
    an array and number of splits
    """
    return karmarkar_karp(a, num_parts=n).partition
