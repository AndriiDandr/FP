"""Мутабельна модель «до» переходу на immutable — лише для порівняння в тестах."""

from __future__ import annotations

from typing import Any

TAG_DISCOUNTS = {
    "new": 1.0,
    "promo": 0.9,
    "sale": 0.8,
    "bestseller": 1.0,
    "fragile": 1.0,
}


def make_record_dict(id: int, sku: str, price: float) -> dict[str, Any]:
    """Складський запис як звичайний dict зі списком, множиною і вкладеним dict."""
    return {
        "id": id,
        "product": {"sku": sku, "price": price},
        "batches": [],
        "tags": set(),
        "supplier": {},
        "active": True,
    }


def restock_inplace(record: dict[str, Any], amount: int) -> None:
    """Мутує список партій."""
    record["batches"].append(amount)


def add_tag_inplace(record: dict[str, Any], tag: str) -> None:
    """Мутує множину тегів."""
    record["tags"].add(tag)


def change_price_inplace(record: dict[str, Any], price: float) -> None:
    """Мутує вкладений словник товару."""
    record["product"]["price"] = price


def stock_value_dict(record: dict[str, Any]) -> float:
    """Вартість без кешу: щоразу перераховується."""
    quantity = 0
    for amount in record["batches"]:
        quantity += amount
    factor = 1.0
    for tag in record["tags"]:
        factor *= TAG_DISCOUNTS[tag]
    return float(quantity * record["product"]["price"] * factor)
