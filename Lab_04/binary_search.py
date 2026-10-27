"""Варіант 4: рекурсивний бінарний пошук у відсортованій незмінній послідовності.

База рекурсії: порожній діапазон [lo, hi) — значення відсутнє. Крок: порівняти з
серединою і продовжити пошук в одній половині. Усі функції чисті, послідовність
не змінюється; tuple хешований, тому пошук по ньому можна мемоізувати.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache


def binary_search(
    xs: Sequence[int], target: int, lo: int = 0, hi: int | None = None
) -> int:
    """Індекс target у відсортованій xs або -1; рекурсія по півінтервалу [lo, hi)."""
    if hi is None:
        hi = len(xs)
    if lo >= hi:
        return -1
    mid = (lo + hi) // 2
    if xs[mid] == target:
        return mid
    if xs[mid] < target:
        return binary_search(xs, target, mid + 1, hi)
    return binary_search(xs, target, lo, mid)


def binary_search_iter(xs: Sequence[int], target: int) -> int:
    """Ітеративна альтернатива: ті самі межі в циклі, без кадрів стеку."""
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return -1


def lower_bound(
    xs: Sequence[int], target: int, lo: int = 0, hi: int | None = None
) -> int:
    """Перший індекс i, де xs[i] >= target (рекурсивно); для дублікатів."""
    if hi is None:
        hi = len(xs)
    if lo >= hi:
        return lo
    mid = (lo + hi) // 2
    if xs[mid] < target:
        return lower_bound(xs, target, mid + 1, hi)
    return lower_bound(xs, target, lo, mid)


def upper_bound(
    xs: Sequence[int], target: int, lo: int = 0, hi: int | None = None
) -> int:
    """Перший індекс i, де xs[i] > target (рекурсивно)."""
    if hi is None:
        hi = len(xs)
    if lo >= hi:
        return lo
    mid = (lo + hi) // 2
    if xs[mid] <= target:
        return upper_bound(xs, target, mid + 1, hi)
    return upper_bound(xs, target, lo, mid)


def count_occurrences(xs: Sequence[int], target: int) -> int:
    """Кількість входжень target: різниця меж upper_bound і lower_bound."""
    return upper_bound(xs, target) - lower_bound(xs, target)


def search_depth(
    xs: Sequence[int], target: int, lo: int = 0, hi: int | None = None
) -> int:
    """Кількість рекурсивних викликів до відповіді — не більше ~log2(n) + 1."""
    if hi is None:
        hi = len(xs)
    if lo >= hi:
        return 1
    mid = (lo + hi) // 2
    if xs[mid] == target:
        return 1
    if xs[mid] < target:
        return 1 + search_depth(xs, target, mid + 1, hi)
    return 1 + search_depth(xs, target, lo, mid)


def is_sorted(xs: Sequence[int]) -> bool:
    """Перевірка відсортованості без зміни послідовності."""
    return all(a <= b for a, b in zip(xs, xs[1:], strict=False))


@lru_cache(maxsize=10_000)
def cached_search(xs: tuple[int, ...], target: int) -> int:
    """Мемоізований пошук: повторний запит (xs, target) береться з кешу."""
    if not is_sorted(xs):
        raise ValueError("sequence must be sorted")
    return binary_search(xs, target)


def linear_search(xs: Sequence[int], target: int) -> int:
    """Лінійний пошук O(n) — для порівняння часу з бінарним O(log n)."""
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1
