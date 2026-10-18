"""Демонстрація pure-оновлень складського запису (лише друк, логіка в core/model)."""

from __future__ import annotations

from typing import Any

from core import (
    add_tag,
    change_price,
    index_by_record,
    restock,
    stock_value,
    with_supplier,
)
from model import Product, make_record


def main() -> None:
    """Створює запис, виконує три pure-оновлення і показує, що оригінал не змінився."""
    r0 = make_record(
        1,
        Product("LAP-01", "Laptop Lenovo", 24_999.0),
        (4,),
        frozenset({"new"}),
        name="TechImport",
    )
    r1 = restock(r0, 6)
    r2 = add_tag(change_price(r1, 23_999.0), "promo")
    r3 = with_supplier(r2, city="Kyiv")

    for name, r in [("r0", r0), ("r1", r1), ("r2", r2), ("r3", r3)]:
        print(
            f"{name}: batches={r.batches} price={r.product.price:.2f} "
            f"tags={sorted(r.tags)} value={stock_value(r):.2f}"
        )
    print("r0 supplier:", dict(r0.supplier), "| r3 supplier:", dict(r3.supplier))
    print("r0 is r3:", r0 is r3, "| r0 unchanged:", r0.batches == (4,))
    print("cache:", stock_value.cache_info())
    index = index_by_record((r0, r2))
    print(
        "as dict keys:", len(index), "records ->", [round(v, 2) for v in index.values()]
    )
    supplier: Any = r0.supplier
    try:
        supplier["name"] = "x"
    except TypeError as e:
        print("supplier read-only:", e)


if __name__ == "__main__":
    main()
