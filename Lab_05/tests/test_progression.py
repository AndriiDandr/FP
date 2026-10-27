import math
from itertools import islice

import pytest
from hypothesis import given
from hypothesis import strategies as st
from progression import (
    MAX_TERMS,
    ProgressionSummary,
    above,
    closed_form_sum,
    geometric,
    geometric_accumulate,
    nth_term,
    running_products,
    running_sums,
    summarize_up_to,
    up_to,
)
from streams import take


def test_first_terms(doubling: tuple[float, float]) -> None:
    q0, r = doubling
    assert take(6, geometric(q0, r)) == [1, 2, 4, 8, 16, 32]
    assert take(4, geometric(5, -1)) == [5, -5, 5, -5]
    assert take(3, geometric(0, 7)) == [0, 0, 0]


def test_accumulate_version_matches_generator() -> None:
    assert take(10, geometric_accumulate(3, 2)) == take(10, geometric(3, 2))
    assert take(5, geometric_accumulate(1, 0.5)) == [1, 0.5, 0.25, 0.125, 0.0625]


def test_up_to_threshold(doubling: tuple[float, float]) -> None:
    q0, r = doubling
    assert list(up_to(100, geometric(q0, r))) == [1, 2, 4, 8, 16, 32, 64]
    assert list(up_to(0.5, geometric(q0, r))) == []
    assert list(up_to(10, geometric(-1, 3))) == [-1, -3, -9]


def test_above_for_decaying() -> None:
    assert list(above(0.1, geometric(1, 0.5))) == [1, 0.5, 0.25, 0.125]
    assert list(above(2, geometric(1, 0.5))) == []


def test_running_sum_and_product(doubling: tuple[float, float]) -> None:
    q0, r = doubling
    terms = up_to(16, geometric(q0, r))
    assert list(running_sums(terms)) == [1, 3, 7, 15, 31]
    assert take(4, running_products(geometric(q0, r))) == [1, 2, 8, 64]
    assert list(running_sums([])) == []


def test_closed_forms() -> None:
    assert nth_term(3, 2, 5) == 96
    assert closed_form_sum(3, 2, 8) == pytest.approx(sum(take(8, geometric(3, 2))))
    assert closed_form_sum(4, 1, 5) == 20
    assert closed_form_sum(4, 3, 0) == 0


def test_summary() -> None:
    assert summarize_up_to(3, 2, 1000) == ProgressionSummary(9, 768, 1533, 3**9 * 2**36)
    assert summarize_up_to(5, 2, 1) == ProgressionSummary(0, 0.0, 0.0, 0.0)


def test_infinite_case_is_bounded() -> None:
    assert len(list(up_to(10, geometric(1, 1)))) == MAX_TERMS
    assert len(list(up_to(10, geometric(1, 1), max_terms=50))) == 50
    assert summarize_up_to(0, 5, 1, max_terms=7).terms == 7


def test_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        list(up_to(-1, geometric(1, 2)))
    with pytest.raises(ValueError):
        list(above(0, geometric(1, 0.5)))
    with pytest.raises(ValueError):
        nth_term(1, 2, -1)
    with pytest.raises(ValueError):
        closed_form_sum(1, 2, -1)


ratios = st.sampled_from([-3, -2, -1, 0, 1, 2, 3])
starts = st.integers(min_value=-20, max_value=20)


@given(starts, ratios, st.integers(min_value=0, max_value=15))
def test_property_stream_matches_formula(q0: int, r: int, n: int) -> None:
    terms = take(n, geometric(q0, r))
    assert terms == [nth_term(q0, r, i) for i in range(n)]
    assert sum(terms) == pytest.approx(closed_form_sum(q0, r, n))


@given(starts, ratios, st.integers(min_value=1, max_value=12))
def test_property_running_product_formula(q0: int, r: int, n: int) -> None:
    last = list(islice(running_products(geometric(q0, r)), n))[-1]
    assert last == q0**n * r ** (n * (n - 1) // 2)


@given(st.floats(min_value=0, max_value=1e6, allow_nan=False))
def test_property_up_to_respects_limit(limit: float) -> None:
    terms = list(up_to(limit, geometric(1, 2)))
    assert all(abs(q) <= limit for q in terms)
    assert len(terms) == (math.floor(math.log2(limit)) + 1 if limit >= 1 else 0)
