"""Чисті бізнес-функції над незмінною моделлю складу (варіант 4).

Жодна функція не змінює вхідні об'єкти: кожне оновлення повертає новий StockRecord,
вартість залишку кешується через lru_cache (StockRecord хешований).
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from typing import Any

from model import StockRecord, Tag

TAG_DISCOUNTS: Mapping[Tag, float] = MappingProxyType(
    {"new": 1.0, "promo": 0.9, "sale": 0.8, "bestseller": 1.0, "fragile": 1.0}
)


def discount_factor(tags: frozenset[Tag]) -> float:
    """Добуток коефіцієнтів знижки всіх тегів (порожня множина → 1.0)."""
    factor = 1.0
    for tag in tags:
        factor *= TAG_DISCOUNTS[tag]
    return factor


@lru_cache(maxsize=1024)
def stock_value(record: StockRecord) -> float:
    """Вартість залишку = кількість × ціна × коефіцієнт знижки. Кешується."""
    return record.quantity() * record.product.price * discount_factor(record.tags)


def restock(record: StockRecord, amount: int) -> StockRecord:
    """Pure update: поповнення залишку новою партією."""
    return record.restock(amount)


def change_price(record: StockRecord, price: float) -> StockRecord:
    """Pure update: новий запис із новою ціною товару."""
    return record.change_price(price)


def add_tag(record: StockRecord, tag: Tag) -> StockRecord:
    """Pure update: новий запис із доданим тегом."""
    return record.add_tag(tag)


def with_supplier(record: StockRecord, **updates: str) -> StockRecord:
    """Pure update: новий запис із новою read-only meta постачальника."""
    merged = {**record.supplier, **updates}
    return StockRecord(
        record.id,
        record.product,
        record.batches,
        record.tags,
        MappingProxyType(merged),
        record.active,
    )


def recalculate(record: StockRecord) -> tuple[StockRecord, float]:
    """Повертає той самий запис і його вартість (кешовану)."""
    return record, stock_value(record)


def index_by_record(records: tuple[StockRecord, ...]) -> Mapping[StockRecord, float]:
    """Запис як ключ словника (хешованість frozen dataclass) → вартість залишку."""
    return MappingProxyType({r: stock_value(r) for r in records})


def freeze(obj: Any) -> Any:
    """Глибоке заморожування: dict → MappingProxyType, set → frozenset, list → tuple."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, set | frozenset):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, list | tuple):
        return tuple(freeze(x) for x in obj)
    return obj
