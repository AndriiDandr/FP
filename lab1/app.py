import json
import sys
import time
from datetime import datetime
from pathlib import Path

from core import (
    Item,
    Receipt,
    accept_positive_qty,
    compose,
    make_cart_processor,
    make_category_discount,
    make_fixed_coupon,
    make_percent_coupon,
    make_vat,
    stamp_total,
)

CATEGORY_RATES = {"electronics": 0.05, "books": 0.10, "food": 0.0, "clothes": 0.15}
COUPON_PERCENT = 10
VAT_RATE = 0.20


def load_cart(path: Path) -> list[Item]:
    with path.open(encoding="utf-8") as f:
        data: list[Item] = json.load(f)
    return data


def render_report(receipt: Receipt, stamped_at: float) -> str:
    header = (
        f"{'Товар':<22}{'Категорія':<13}{'Ціна':>9}{'К-сть':>7}"
        f"{'Сума':>10}{'Знижка':>8}{'Після':>10}"
    )
    lines = [header, "-" * 79]
    for p in receipt["items"]:
        lines.append(
            f"{p['name']:<22}{p['category']:<13}{p['price']:>9.2f}{p['qty']:>7}"
            f"{p['line_total']:>10.2f}{p['discount_rate'] * 100:>7.0f}%"
            f"{p['discounted_total']:>10.2f}"
        )
    lines += [
        "-" * 79,
        f"{'Subtotal:':<24}{receipt['subtotal']:>12.2f}",
        f"{'Категоріальна знижка:':<24}{-receipt['category_discount']:>12.2f}",
        f"{'Купон:':<24}{-receipt['coupon_discount']:>12.2f}",
        f"{'ПДВ:':<24}{receipt['vat']:>+12.2f}",
        f"{'До сплати:':<24}{receipt['total']:>12.2f}",
        f"Час розрахунку: {datetime.fromtimestamp(stamped_at):%Y-%m-%d %H:%M:%S}",
    ]
    return "\n".join(lines)


def run(cart: list[Item]) -> None:
    processor = make_cart_processor(
        accept=accept_positive_qty,
        category_discount=make_category_discount(CATEGORY_RATES),
        apply_coupon=make_percent_coupon(COUPON_PERCENT),
        apply_tax=make_vat(VAT_RATE),
    )
    receipt = processor(cart)
    _, stamped_at = stamp_total(receipt["total"], time.time)
    print("=== Кошик: знижка 10% за купоном, ПДВ 20% ===")
    print(render_report(receipt, stamped_at))

    combo_coupon = compose(make_fixed_coupon(100, min_amount=1000), make_percent_coupon(5))
    alt = make_cart_processor(
        accept=lambda it: accept_positive_qty(it) and it["category"] != "food",
        category_discount=make_category_discount({"electronics": 0.10}),
        apply_coupon=combo_coupon,
        apply_tax=make_vat(VAT_RATE),
    )
    alt_receipt = alt(cart)
    print()
    print("=== Інша політика: без food, купон 5% + 100 грн від 1000 грн ===")
    print(render_report(alt_receipt, stamped_at))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cart_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cart.json")
    run(load_cart(cart_path))
