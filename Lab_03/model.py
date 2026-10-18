from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import NamedTuple


def make_meta(**kwargs: str) -> Mapping[str, str]:
    return MappingProxyType(dict(kwargs))


def freeze(obj: object) -> object:
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, set | frozenset):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, list | tuple):
        return tuple(freeze(x) for x in obj)
    return obj


class Movement(NamedTuple):
    delta: int
    reason: str


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    price: float
    category: str
    tags: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class StockRecord:
    product: Product
    quantity: int
    min_quantity: int
    movements: tuple[Movement, ...] = ()
    supplier: Mapping[str, str] = field(default_factory=make_meta, hash=False)

    def stock_value(self) -> float:
        return self.product.price * self.quantity

    def needs_reorder(self) -> bool:
        return self.quantity < self.min_quantity


def make_record(
    *,
    sku: str,
    name: str,
    price: float,
    category: str,
    quantity: int,
    min_quantity: int,
    tags: Iterable[str] = (),
    supplier: Mapping[str, str] | None = None,
) -> StockRecord:
    return StockRecord(
        product=Product(sku, name, price, category, frozenset(tags)),
        quantity=quantity,
        min_quantity=min_quantity,
        supplier=make_meta(**dict(supplier or {})),
    )
