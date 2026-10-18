from typing import Any


def make_mutable_record(
    sku: str, price: float, quantity: int, min_quantity: int
) -> dict[str, Any]:
    return {
        "product": {"sku": sku, "price": price, "tags": set()},
        "quantity": quantity,
        "min_quantity": min_quantity,
        "movements": [],
        "supplier": {"name": "Supplier"},
    }


def restock_in_place(record: dict[str, Any], amount: int) -> None:
    record["quantity"] += amount
    record["movements"].append((amount, "restock"))


def change_price_in_place(record: dict[str, Any], new_price: float) -> None:
    record["product"]["price"] = new_price


def add_tag_in_place(record: dict[str, Any], tag: str) -> None:
    record["product"]["tags"].add(tag)
