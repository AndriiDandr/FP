import bisect
import math
import timeit

import pytest
from binary_search import (
    binary_search,
    binary_search_iter,
    cached_search,
    count_occurrences,
    is_sorted,
    linear_search,
    lower_bound,
    search_depth,
    upper_bound,
)
from hypothesis import given
from hypothesis import strategies as st

XS = (1, 3, 5, 7, 9, 11, 13)


@pytest.mark.parametrize(
    ("xs", "target", "expected"),
    [
        ((), 5, -1),
        ((5,), 5, 0),
        ((5,), 4, -1),
        ((1, 2), 1, 0),
        ((1, 2), 2, 1),
        ((1, 2), 3, -1),
    ],
)
def test_edge_cases(xs: tuple[int, ...], target: int, expected: int) -> None:
    assert binary_search(xs, target) == expected
    assert binary_search_iter(xs, target) == expected


@pytest.mark.parametrize("target", XS)
def test_found_values(target: int) -> None:
    assert XS[binary_search(XS, target)] == target
    assert binary_search(XS, target) == binary_search_iter(XS, target)


@pytest.mark.parametrize("target", [0, 2, 8, 14, -5, 100])
def test_missing_values(target: int) -> None:
    assert binary_search(XS, target) == -1
    assert binary_search_iter(XS, target) == -1
    assert linear_search(XS, target) == -1


def test_duplicates_bounds_and_count() -> None:
    xs = (1, 3, 3, 3, 7, 9)
    assert lower_bound(xs, 3) == 1
    assert upper_bound(xs, 3) == 4
    assert count_occurrences(xs, 3) == 3
    assert count_occurrences(xs, 4) == 0
    assert xs[binary_search(xs, 3)] == 3
    assert lower_bound(xs, 100) == len(xs)
    assert upper_bound(xs, -1) == 0


def test_input_not_mutated() -> None:
    xs = [1, 2, 4, 8, 16]
    snapshot = list(xs)
    binary_search(xs, 8)
    lower_bound(xs, 3)
    count_occurrences(xs, 4)
    assert xs == snapshot


def test_recursion_depth_is_logarithmic() -> None:
    xs = tuple(range(1_000_000))
    for target in (0, 500_000, 999_999, -1):
        assert search_depth(xs, target) <= math.floor(math.log2(len(xs))) + 2


def test_cache_info_and_clear() -> None:
    cached_search.cache_clear()
    assert cached_search(XS, 7) == 3
    assert cached_search(XS, 7) == 3
    info = cached_search.cache_info()
    assert info.hits == 1 and info.misses == 1
    cached_search.cache_clear()
    assert cached_search.cache_info().currsize == 0


def test_cached_search_rejects_unsorted() -> None:
    assert is_sorted(XS) and not is_sorted((3, 1, 2))
    with pytest.raises(ValueError):
        cached_search((3, 1, 2), 1)


def test_binary_faster_than_linear() -> None:
    xs = tuple(range(200_000))
    t_binary = timeit.timeit(lambda: binary_search(xs, 199_999), number=50)
    t_linear = timeit.timeit(lambda: linear_search(xs, 199_999), number=50)
    assert t_binary < t_linear


@given(st.lists(st.integers(-1000, 1000), max_size=200), st.integers(-1100, 1100))
def test_property_recursive_equals_iterative(values: list[int], target: int) -> None:
    xs = tuple(sorted(values))
    i = binary_search(xs, target)
    assert (i == -1) == (target not in xs)
    assert i == -1 or xs[i] == target
    assert (binary_search_iter(xs, target) == -1) == (i == -1)


@given(st.lists(st.integers(-50, 50), max_size=100), st.integers(-60, 60))
def test_property_bounds_match_bisect(values: list[int], target: int) -> None:
    xs = tuple(sorted(values))
    assert lower_bound(xs, target) == bisect.bisect_left(xs, target)
    assert upper_bound(xs, target) == bisect.bisect_right(xs, target)
    assert count_occurrences(xs, target) == xs.count(target)
