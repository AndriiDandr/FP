"""Незмінна модель складу товарів (варіант 4).

Product і StockRecord — frozen dataclass зі slots; партії поповнення у tuple,
теги у frozenset, метадані постачальника — MappingProxyType поверх копії словника.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Literal

Tag = Literal["new", "promo", "sale", "bestseller", "fragile"]


@dataclass(frozen=True, slots=True)
class Product:
    """Товар: артикул, назва і ціна за одиницю."""

    sku: str
    name: str
    price: float

    def with_price(self, price: float) -> Product:
        """Новий товар з іншою ціною."""
        return replace(self, price=price)


@dataclass(frozen=True, slots=True)
class StockRecord:
    """Складський запис: товар, партії (tuple), теги (frozenset), постачальник."""

    id: int
    product: Product
    batches: tuple[int, ...]
    tags: frozenset[Tag]
    supplier: Mapping[str, str] = field(hash=False)
    active: bool = True

    def quantity(self) -> int:
        """Залишок на складі — сума всіх партій."""
        return sum(self.batches)

    def restock(self, amount: int) -> StockRecord:
        """Новий запис із доданою партією поповнення."""
        return replace(self, batches=self.batches + (amount,))

    def change_price(self, price: float) -> StockRecord:
        """Новий запис із новою ціною товару."""
        return replace(self, product=self.product.with_price(price))

    def add_tag(self, tag: Tag) -> StockRecord:
        """Новий запис із доданим тегом."""
        return replace(self, tags=self.tags | frozenset({tag}))

    def deactivate(self) -> StockRecord:
        """Новий запис, знятий з продажу."""
        return replace(self, active=False)


def make_meta(**kwargs: str) -> Mapping[str, str]:
    """Read-only view над КОПІЄЮ словника, щоб ніхто не тримав посилання на оригінал."""
    return MappingProxyType(dict(kwargs))


def make_record(
    id: int,
    product: Product,
    batches: tuple[int, ...] = (),
    tags: frozenset[Tag] = frozenset(),
    **supplier: str,
) -> StockRecord:
    """Зручний конструктор складського запису з read-only метаданими постачальника."""
    return StockRecord(id, product, batches, tags, make_meta(**supplier))
