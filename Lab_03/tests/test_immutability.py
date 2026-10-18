from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from core import (
    add_tag,
    change_price,
    freeze,
    index_by_record,
    restock,
    stock_value,
    with_supplier,
)
from hypothesis import given
from hypothesis import strategies as st
from model import Product, StockRecord, make_meta, make_record


def test_restock_returns_new_record(record: StockRecord) -> None:
    before = (record.batches, record.tags, dict(record.supplier))
    new = restock(record, 5)
    assert (record.batches, record.tags, dict(record.supplier)) == before
    assert new is not record
    assert new.batches == (4, 6, 5)
    assert new.quantity() == record.quantity() + 5


def test_change_price_returns_new_record(record: StockRecord) -> None:
    new = change_price(record, 900.0)
    assert record.product.price == 1_000.0
    assert new.product.price == 900.0
    assert new.product is not record.product
    assert new.batches is record.batches


def test_add_tag_returns_new_record(record: StockRecord) -> None:
    new = add_tag(record, "promo")
    assert record.tags == frozenset({"new"})
    assert new.tags == frozenset({"new", "promo"})
    assert new.deactivate().active is False and record.active is True


def test_frozen_fields_cannot_be_assigned(record: StockRecord) -> None:
    target: Any = record
    with pytest.raises(FrozenInstanceError):
        target.id = 2
    with pytest.raises(FrozenInstanceError):
        target.product.price = 1.0


def test_supplier_is_read_only(record: StockRecord) -> None:
    supplier: Any = record.supplier
    with pytest.raises(TypeError):
        supplier["name"] = "changed"
    assert record.supplier["name"] == "TechImport"


def test_make_meta_copies_source() -> None:
    raw = {"k": "v"}
    meta = make_meta(**raw)
    raw["k"] = "changed"
    assert meta["k"] == "v"


def test_with_supplier_creates_new_mapping(record: StockRecord) -> None:
    new = with_supplier(record, city="Lviv", phone="123")
    assert dict(new.supplier) == {"name": "TechImport", "city": "Lviv", "phone": "123"}
    assert dict(record.supplier) == {"name": "TechImport", "city": "Kyiv"}


def test_hashability_and_dict_key(record: StockRecord) -> None:
    other = add_tag(record, "sale")
    assert len({record, other, add_tag(record, "sale")}) == 2
    index = index_by_record((record, other))
    assert index[record] == pytest.approx(10_000.0)
    assert index[other] == pytest.approx(10_000.0 * 0.8)
    assert set(index) == {record, other}


def test_stock_value_and_cache(record: StockRecord) -> None:
    stock_value.cache_clear()
    assert stock_value(record) == pytest.approx(10 * 1_000.0)
    stock_value(record)
    info = stock_value.cache_info()
    assert info.hits == 1 and info.misses == 1
    assert stock_value(add_tag(record, "promo")) == pytest.approx(10_000.0 * 0.9)


def test_freeze_deep() -> None:
    frozen = freeze({"a": [1, {2, 3}], "b": {"c": [4]}})
    with pytest.raises(TypeError):
        frozen["a"] = 0
    assert frozen["a"] == (1, frozenset({2, 3}))
    with pytest.raises(TypeError):
        frozen["b"]["c"] = 0
    assert frozen["b"]["c"] == (4,)


products_st = st.builds(
    Product,
    st.text(min_size=1, max_size=6),
    st.text(min_size=1, max_size=10),
    st.floats(min_value=0, max_value=1e5, allow_nan=False),
)
records_st = st.builds(
    make_record,
    st.integers(min_value=1),
    products_st,
    st.tuples(st.integers(0, 100), st.integers(0, 100)),
    st.frozensets(st.sampled_from(["new", "promo", "sale", "bestseller", "fragile"])),
)


@given(records_st, st.integers(min_value=1, max_value=500))
def test_property_restock_pure(r: StockRecord, amount: int) -> None:
    before = (r.batches, r.tags, dict(r.supplier))
    new = r.restock(amount)
    assert (r.batches, r.tags, dict(r.supplier)) == before
    assert new.batches == r.batches + (amount,)
    assert new.quantity() == r.quantity() + amount


@given(records_st)
def test_property_hash_consistent_with_eq(r: StockRecord) -> None:
    twin = StockRecord(r.id, r.product, r.batches, r.tags, r.supplier, r.active)
    assert twin == r and hash(twin) == hash(r)
    assert stock_value(r) == stock_value(twin)
