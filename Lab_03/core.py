from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from functools import lru_cache, reduce
from types import MappingProxyType

from model import Movement, StockRecord, make_meta

PriceRule = Callable[[StockRecord], float]


def restock(record: StockRecord, amount: int) -> StockRecord:
    if amount <= 0:
        raise ValueError("amount must be positive")
    return replace(
        record,
        quantity=record.quantity + amount,
        movements=record.movements + (Movement(amount, "restock"),),
    )


def ship(record: StockRecord, amount: int) -> StockRecord:
    if amount <= 0 or amount > record.quantity:
        raise ValueError("invalid shipment amount")
    return replace(
        record,
        quantity=record.quantity - amount,
        movements=record.movements + (Movement(-amount, "ship"),),
    )


def change_price(record: StockRecord, new_price: float) -> StockRecord:
    if new_price < 0:
        raise ValueError("price must be non-negative")
    return replace(record, product=replace(record.product, price=new_price))


def add_tag(record: StockRecord, tag: str) -> StockRecord:
    tags = record.product.tags | frozenset({tag})
    return replace(record, product=replace(record.product, tags=tags))


def remove_tag(record: StockRecord, tag: str) -> StockRecord:
    tags = record.product.tags - frozenset({tag})
    return replace(record, product=replace(record.product, tags=tags))


def update_supplier(record: StockRecord, **changes: str) -> StockRecord:
    return replace(record, supplier=make_meta(**{**record.supplier, **changes}))


def supplier_name(meta: Mapping[str, str]) -> str:
    return meta.get("name", "unknown")


def total_value(records: Sequence[StockRecord]) -> float:
    return reduce(lambda acc, r: acc + r.stock_value(), records, 0.0)


def to_reorder(records: Sequence[StockRecord]) -> tuple[StockRecord, ...]:
    return tuple(filter(lambda r: r.needs_reorder(), records))


def top_valuable(records: Sequence[StockRecord], n: int = 3) -> tuple[StockRecord, ...]:
    return tuple(sorted(records, key=lambda r: r.stock_value(), reverse=True)[:n])


def with_tag(records: Sequence[StockRecord], tag: str) -> tuple[StockRecord, ...]:
    return tuple(r for r in records if tag in r.product.tags)


def index_by_sku(records: Sequence[StockRecord]) -> Mapping[str, StockRecord]:
    return MappingProxyType({r.product.sku: r for r in records})


def make_category_discount(rates: Mapping[str, float]) -> PriceRule:
    frozen_rates = MappingProxyType(dict(rates))
    return lambda r: r.product.price * (1 - frozen_rates.get(r.product.category, 0.0))


def apply_price_rule(
    records: Sequence[StockRecord], rule: PriceRule
) -> tuple[StockRecord, ...]:
    return tuple(change_price(r, round(rule(r), 2)) for r in records)


@lru_cache(maxsize=256)
def reorder_cost(record: StockRecord) -> float:
    missing = max(record.min_quantity * 2 - record.quantity, 0)
    return round(missing * record.product.price, 2)
