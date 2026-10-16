from collections.abc import Callable, Iterable, Mapping
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Item(TypedDict):
    name: str
    price: float
    qty: int
    category: str


class PricedItem(TypedDict):
    name: str
    price: float
    qty: int
    category: str
    line_total: float
    discount_rate: float
    discounted_total: float


class Receipt(TypedDict):
    items: list[PricedItem]
    subtotal: float
    category_discount: float
    after_category: float
    coupon_discount: float
    after_coupon: float
    vat: float
    total: float


ItemFilterFn = Callable[[Item], bool]
CategoryDiscountFn = Callable[[Item], float]
CouponFn = Callable[[float], float]
TaxFn = Callable[[float], float]
NowFn = Callable[[], float]
CartProcessor = Callable[[Iterable[Item]], Receipt]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def identity(x: A) -> A:
    return x


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def line_total(item: Item) -> float:
    return item["price"] * item["qty"]


def cart_subtotal(items: Iterable[Item]) -> float:
    return sum(line_total(it) for it in items)


def price_item(item: Item, discount_rate: float) -> PricedItem:
    total = line_total(item)
    return {
        "name": item["name"],
        "price": item["price"],
        "qty": item["qty"],
        "category": item["category"],
        "line_total": total,
        "discount_rate": discount_rate,
        "discounted_total": total * (1 - discount_rate),
    }


def with_qty(item: Item, qty: int) -> Item:
    return {**item, "qty": qty}


def without_category(items: Iterable[Item], category: str) -> list[Item]:
    return [it for it in items if it["category"] != category]


def scale_prices(items: Iterable[Item], k: float) -> list[Item]:
    return [{**it, "price": it["price"] * k} for it in items]


def make_category_discount(rates: Mapping[str, float]) -> CategoryDiscountFn:
    frozen = dict(rates)
    return lambda item: frozen.get(item["category"], 0.0)


def make_percent_coupon(percent: float) -> CouponFn:
    return lambda amount: amount * (1 - percent / 100)


def make_fixed_coupon(value: float, min_amount: float = 0.0) -> CouponFn:
    return lambda amount: max(amount - value, 0.0) if amount >= min_amount else amount


def make_vat(rate: float) -> TaxFn:
    return lambda amount: amount * (1 + rate)


def accept_positive_qty(item: Item) -> bool:
    return item["qty"] > 0 and item["price"] >= 0


def make_cart_processor(
    *,
    accept: ItemFilterFn,
    category_discount: CategoryDiscountFn,
    apply_coupon: CouponFn,
    apply_tax: TaxFn,
) -> CartProcessor:
    def process(items: Iterable[Item]) -> Receipt:
        priced = [price_item(it, category_discount(it)) for it in items if accept(it)]
        subtotal = sum(p["line_total"] for p in priced)
        after_category = sum(p["discounted_total"] for p in priced)
        after_coupon = apply_coupon(after_category)
        total = apply_tax(after_coupon)
        return {
            "items": priced,
            "subtotal": subtotal,
            "category_discount": subtotal - after_category,
            "after_category": after_category,
            "coupon_discount": after_category - after_coupon,
            "after_coupon": after_coupon,
            "vat": total - after_coupon,
            "total": total,
        }

    return process


def process_cart_pure(
    items: Iterable[Item],
    *,
    category_rates: Mapping[str, float],
    coupon_percent: float,
    vat_rate: float,
) -> Receipt:
    processor = make_cart_processor(
        accept=accept_positive_qty,
        category_discount=make_category_discount(category_rates),
        apply_coupon=make_percent_coupon(coupon_percent),
        apply_tax=make_vat(vat_rate),
    )
    return processor(items)


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    return total, now()
