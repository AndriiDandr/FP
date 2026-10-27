"""Демо ЛР4: бінарний пошук, порівняння часу, мемоізація, базові алгоритми."""

from __future__ import annotations

import sys
import timeit

from algorithms import (
    Node,
    bfs_level_order,
    fib,
    fib_iter,
    fib_naive,
    inorder,
    quicksort,
)
from binary_search import (
    binary_search,
    binary_search_iter,
    cached_search,
    count_occurrences,
    linear_search,
    lower_bound,
    search_depth,
)


def main() -> None:
    """Друкує результати та таблицю часу (лише I/O, обчислення чисті)."""
    xs = (1, 3, 3, 3, 7, 9, 12, 15, 21)
    for target in (7, 3, 1, 21, 4, 100):
        print(
            f"target={target:>3}: recursive={binary_search(xs, target):>2} "
            f"iterative={binary_search_iter(xs, target):>2} "
            f"lower_bound={lower_bound(xs, target)} "
            f"count={count_occurrences(xs, target)}"
        )

    big = tuple(range(0, 2_000_000, 2))
    target = 1_999_998
    t_rec = timeit.timeit(lambda: binary_search(big, target), number=1000)
    t_iter = timeit.timeit(lambda: binary_search_iter(big, target), number=1000)
    t_lin = timeit.timeit(lambda: linear_search(big, target), number=10) * 100
    print(f"n={len(big)}, 1000 searches:")
    print(f"  recursive : {t_rec * 1e3:.2f} ms")
    print(f"  iterative : {t_iter * 1e3:.2f} ms")
    print(f"  linear    : {t_lin * 1e3:.1f} ms")
    print("recursion depth:", search_depth(big, target), "calls")

    cached_search.cache_clear()
    t_first = timeit.timeit(lambda: cached_search(big, target), number=1)
    t_cached = timeit.timeit(lambda: cached_search(big, target), number=1)
    print(
        f"cached_search first: {t_first * 1e3:.2f} ms, repeat: {t_cached * 1e3:.4f} ms"
    )
    print("cache_info:", cached_search.cache_info())

    fib.cache_clear()
    print("fib(30) cached:", f"{timeit.timeit(lambda: fib(30), number=1) * 1e3:.3f} ms")
    print(
        "fib(30) naive :",
        f"{timeit.timeit(lambda: fib_naive(30), number=1) * 1e3:.1f} ms",
    )
    print("fib(90) ==", fib(90), "iter:", fib_iter(90))

    print("quicksort:", quicksort([3, 1, 4, 1, 5, 9, 2, 6]))
    t = Node(4, Node(2, Node(1), Node(3)), Node(6, None, Node(7)))
    print("inorder:", list(inorder(t)), "bfs:", bfs_level_order(t))
    print("recursion limit:", sys.getrecursionlimit())


if __name__ == "__main__":
    main()
