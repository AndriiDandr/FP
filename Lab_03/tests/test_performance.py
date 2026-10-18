"""Порівняння часу: модель «до» (mutable) і «після» (immutable), --durations=5."""

from core import add_tag, restock, stock_value
from model import StockRecord
from mutable_model import (
    add_tag_inplace,
    make_record_dict,
    restock_inplace,
    stock_value_dict,
)

N = 2_000


def test_mutable_before() -> None:
    r = make_record_dict(1, "LAP-01", 1_000.0)
    for i in range(N):
        restock_inplace(r, 1 + i % 3)
    add_tag_inplace(r, "promo")
    total = sum(stock_value_dict(r) for _ in range(N))
    assert total > 0


def test_immutable_after(record: StockRecord) -> None:
    r = record
    for i in range(N):
        r = restock(r, 1 + i % 3)
    r = add_tag(r, "promo")
    stock_value.cache_clear()
    total = sum(stock_value(r) for _ in range(N))
    assert total > 0
    assert stock_value.cache_info().hits == N - 1
