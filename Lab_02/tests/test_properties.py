import copy

import pytest
from core import (
    Order,
    build_pipeline,
    check_of,
    compose,
    pipe,
    reduce_stats,
    revenue_by_waiter,
    sort_by_check_desc,
    take,
    with_check,
)
from hypothesis import given
from hypothesis import strategies as st

items = st.lists(
    st.fixed_dictionaries(
        {
            "name": st.text(min_size=1, max_size=8),
            "price": st.floats(
                min_value=0, max_value=1000, allow_nan=False, allow_infinity=False
            ),
            "qty": st.integers(min_value=0, max_value=5),
        }
    ),
    max_size=5,
)
orders_strategy = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.integers(min_value=0, max_value=100),
            "waiter": st.sampled_from(["olena", "Taras", " IRYNA ", "bohdan"]),
            "table": st.integers(min_value=0, max_value=35),
            "items": items,
        }
    ),
    max_size=15,
    unique_by=lambda o: o["id"],
)


@given(orders_strategy, st.integers(0, 10), st.floats(0, 500))
def test_pipeline_result_is_sorted_filtered_and_bounded(
    orders: list[Order], top_n: int, threshold: float
) -> None:
    top = build_pipeline(top_n=top_n, threshold=threshold)(orders)
    assert len(top) <= min(top_n, len(orders))
    keys = [(-o["check"], o["id"]) for o in top]
    assert keys == sorted(keys)
    assert all(o["check"] >= threshold for o in top)
    assert all(o["waiter"] == o["waiter"].strip().title() for o in top)


@given(orders_strategy)
def test_pipeline_never_mutates_input(orders: list[Order]) -> None:
    snapshot = copy.deepcopy(orders)
    build_pipeline(top_n=5, threshold=0.0)(orders)
    assert orders == snapshot


@given(orders_strategy, st.floats(1.0, 3.0))
def test_boost_only_raises_checks_of_the_zone(
    orders: list[Order], factor: float
) -> None:
    plain = {o["id"]: o["check"] for o in build_pipeline(100, "vip", 1.0, 0.0)(orders)}
    boosted = {
        o["id"]: o["check"] for o in build_pipeline(100, "vip", factor, 0.0)(orders)
    }
    tables = {o["id"]: o["table"] for o in orders}
    for order_id, check in boosted.items():
        expected = (
            plain[order_id] * factor
            if 21 <= tables[order_id] <= 30
            else plain[order_id]
        )
        assert check == pytest.approx(expected)


@given(orders_strategy)
def test_reduce_stats_matches_direct_computation(orders: list[Order]) -> None:
    checked = list(with_check()(orders))
    stats = reduce_stats(checked)
    checks = [check_of(o) for o in checked]
    assert stats["count"] == len(checks)
    assert stats["sum_checks"] == pytest.approx(sum(checks))
    assert stats["max_check"] == pytest.approx(max(checks, default=0.0))
    assert stats["avg_check"] == pytest.approx(
        sum(checks) / len(checks) if checks else 0.0
    )
    assert sum(revenue_by_waiter(checked).values()) == pytest.approx(sum(checks))


@given(orders_strategy, st.integers(0, 6))
def test_compose_is_pipe_reversed(orders: list[Order], n: int) -> None:
    steps = (with_check(), sort_by_check_desc(), take(n))
    assert list(pipe(*steps)(orders)) == list(compose(*reversed(steps))(orders))
