import copy
from collections.abc import Iterator

import pytest
from core import (
    Order,
    boost_zone,
    build_pipeline,
    check_of,
    check_total,
    compose,
    compose2,
    identity,
    make_zone_resolver,
    min_check,
    normalize_waiters,
    parse_order,
    pipe,
    reduce_stats,
    revenue_by_waiter,
    sort_by_check_desc,
    take,
    with_check,
    zone_of,
)


def test_check_total_sums_price_times_qty() -> None:
    assert check_total([]) == 0.0
    assert check_total([{"name": "a", "price": 10.0, "qty": 2}]) == 20.0
    assert check_total(
        [{"name": "a", "price": 95.0, "qty": 2}, {"name": "b", "price": 20.0, "qty": 1}]
    ) == pytest.approx(210.0)


def test_check_of_prefers_computed_field() -> None:
    order: Order = {"id": 1, "items": [{"name": "a", "price": 10.0, "qty": 1}]}
    assert check_of(order) == 10.0
    assert check_of({**order, "check": 99.0}) == 99.0


def test_zone_resolver() -> None:
    assert zone_of(1) == "hall" and zone_of(10) == "hall"
    assert zone_of(11) == "terrace" and zone_of(25) == "vip"
    assert zone_of(0) == "unknown" and zone_of(99) == "unknown"
    custom = make_zone_resolver({"bar": range(100, 105)})
    assert custom(102) == "bar" and custom(1) == "unknown"


def test_with_check_adds_field_and_keeps_input(orders: list[Order]) -> None:
    result = list(with_check()(orders))
    assert [o["check"] for o in result[:3]] == [210.0, 780.0, 90.0]
    assert all("check" not in o for o in orders)
    assert all(a is not b for a, b in zip(orders, result, strict=True))


def test_boost_zone_applies_only_to_selected_zone(orders: list[Order]) -> None:
    boosted = list(boost_zone("terrace", 1.1)(with_check()(orders)))
    by_id = {o["id"]: o["check"] for o in boosted}
    assert by_id[2] == pytest.approx(858.0)
    assert by_id[1] == 210.0 and by_id[5] == 1200.0
    assert by_id[11] == 0.0


def test_boost_zone_without_check_computes_it() -> None:
    order: Order = {
        "id": 1,
        "table": 21,
        "items": [{"name": "a", "price": 100.0, "qty": 1}],
    }
    assert list(boost_zone("vip", 1.5)([order]))[0]["check"] == 150.0


def test_min_check_filters_small_checks(orders: list[Order]) -> None:
    kept = list(min_check(200.0)(with_check()(orders)))
    assert [o["id"] for o in kept] == [1, 2, 4, 5, 6, 7, 8, 10, 12]
    assert list(min_check(10_000.0)(with_check()(orders))) == []


def test_normalize_waiters() -> None:
    result = list(
        normalize_waiters()(
            [{"id": 1, "waiter": "  OLENA "}, {"id": 2, "waiter": "taras"}]
        )
    )
    assert [o["waiter"] for o in result] == ["Olena", "Taras"]


def test_sort_desc_with_id_tie_break() -> None:
    orders: list[Order] = [
        {"id": 5, "check": 100.0},
        {"id": 2, "check": 300.0},
        {"id": 1, "check": 100.0},
        {"id": 9, "check": 300.0},
    ]
    assert [o["id"] for o in sort_by_check_desc()(orders)] == [2, 9, 1, 5]


def test_take_top_n() -> None:
    orders: list[Order] = [{"id": i} for i in range(5)]
    assert [o["id"] for o in take(2)(orders)] == [0, 1]
    assert len(list(take(10)(orders))) == 5
    assert list(take(0)(orders)) == [] and list(take(-3)(orders)) == []


def test_transforms_are_lazy(orders: list[Order]) -> None:
    for step in (
        with_check(),
        boost_zone("hall", 2.0),
        min_check(0.0),
        normalize_waiters(),
        take(2),
    ):
        assert isinstance(step(orders), Iterator)


def test_pipeline_top_n(orders: list[Order]) -> None:
    top = build_pipeline(top_n=3)(orders)
    assert [o["id"] for o in top] == [8, 5, 2]
    assert [o["check"] for o in top] == pytest.approx([1300.0, 1200.0, 858.0])
    assert [o["waiter"] for o in top] == ["Bohdan", "Olena", "Taras"]


def test_pipeline_tie_break_and_other_zone(orders: list[Order]) -> None:
    ids = [o["id"] for o in build_pipeline(top_n=4)(orders)]
    assert ids == [8, 5, 2, 12]
    vip = build_pipeline(top_n=2, zone="vip", factor=2.0)(orders)
    assert [(o["id"], o["check"]) for o in vip] == [(8, 2600.0), (5, 2400.0)]


def test_pipeline_does_not_mutate_input(orders: list[Order]) -> None:
    snapshot = copy.deepcopy(orders)
    pipeline = build_pipeline()
    pipeline(orders)
    reduce_stats(pipeline(orders))
    revenue_by_waiter(pipeline(orders))
    assert orders == snapshot
    assert all("check" not in o for o in orders)


def test_reduce_stats() -> None:
    stats = reduce_stats(
        [
            {"id": 1, "check": 100.0},
            {"id": 2, "check": 300.0},
            {"id": 3, "check": 200.0},
        ]
    )
    assert stats == {
        "count": 3,
        "sum_checks": 600.0,
        "avg_check": 200.0,
        "max_check": 300.0,
    }


def test_reduce_stats_empty_and_without_check() -> None:
    assert reduce_stats([]) == {
        "count": 0,
        "sum_checks": 0.0,
        "avg_check": 0.0,
        "max_check": 0.0,
    }
    stats = reduce_stats([{"id": 1, "items": [{"name": "a", "price": 50.0, "qty": 3}]}])
    assert stats["sum_checks"] == 150.0 and stats["count"] == 1


def test_revenue_by_waiter(orders: list[Order]) -> None:
    revenue = revenue_by_waiter(build_pipeline(top_n=4)(orders))
    assert revenue == pytest.approx(
        {"Bohdan": 1300.0, "Olena": 1200.0, "Taras": 1716.0}
    )
    assert revenue_by_waiter([]) == {}


def test_compose_and_pipe_order(orders: list[Order]) -> None:
    right_to_left = compose(take(2), sort_by_check_desc(), with_check())
    left_to_right = pipe(with_check(), sort_by_check_desc(), take(2))
    assert list(right_to_left(orders)) == list(left_to_right(orders))
    assert [o["id"] for o in right_to_left(orders)] == [8, 5]
    assert list(compose(identity, with_check())(orders)) == list(with_check()(orders))
    assert list(compose()(orders)) == orders


def test_compose2_generic() -> None:
    length_of_upper = compose2(len, str.upper)
    assert length_of_upper("abc") == 3
    inc_then_str = compose2(str, (1).__add__)
    assert inc_then_str(41) == "42"


def test_parse_order_from_json_like_dict() -> None:
    order = parse_order(
        {
            "id": "7",
            "waiter": "iryna",
            "table": 18,
            "items": [{"name": "паста", "price": "190", "qty": 2}],
        }
    )
    assert order == {
        "id": 7,
        "waiter": "iryna",
        "table": 18,
        "items": [{"name": "паста", "price": 190.0, "qty": 2}],
    }


@pytest.mark.parametrize(
    "raw",
    [
        {"id": 1, "items": "not a list"},
        {"id": 1, "items": [{"name": "x", "price": True, "qty": 1}]},
        {"id": 1, "items": [{"name": "x", "price": 1, "qty": 1.5}]},
        {"id": 1, "items": ["x"]},
    ],
)
def test_parse_order_rejects_bad_input(raw: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        parse_order(raw)
