"""Варіант 4: замовлення ресторану — конвеєр перетворень без мутацій.

Кожна трансформація — функція вищого порядку, що повертає чисту функцію
«послідовність замовлень → послідовність замовлень». Такі функції мають однаковий
тип, тому з них можна зібрати конвеєр через compose / pipe. Записи ніколи не
змінюються на місці: нові словники створюються через {**order, ...}, а список
замовлень на вході читається лише один раз генератором.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from functools import reduce
from itertools import islice
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Item(TypedDict):
    """Позиція чека: назва страви, ціна за одиницю, кількість."""

    name: str
    price: float
    qty: int


class Order(TypedDict, total=False):
    """Замовлення: id, офіціант, столик, позиції; поле check додає конвеєр."""

    id: int
    waiter: str
    table: int
    items: list[Item]
    check: float


class Stats(TypedDict):
    """Підсумок reduce-агрегації за списком замовлень."""

    count: int
    sum_checks: float
    avg_check: float
    max_check: float


Step = Callable[[Iterable[Order]], Iterable[Order]]
Pipeline = Callable[[Iterable[Order]], list[Order]]

DEFAULT_ZONES: Mapping[str, range] = {
    "hall": range(1, 11),
    "terrace": range(11, 21),
    "vip": range(21, 31),
}


# --- композиція ---


def compose(*steps: Step) -> Step:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""
    return lambda orders: reduce(lambda acc, f: f(acc), reversed(steps), orders)


def pipe(*steps: Step) -> Step:
    """Композиція зліва направо: pipe(f, g)(x) == g(f(x)) — читається як конвеєр."""
    return lambda orders: reduce(lambda acc, f: f(acc), steps, orders)


def compose2(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Типізована композиція двох довільних функцій: compose2(f, g)(x) == f(g(x))."""
    return lambda x: f(g(x))


def identity(orders: Iterable[Order]) -> Iterable[Order]:
    """Нейтральний крок конвеєра: compose(identity, f) == f."""
    return orders


# --- допоміжні чисті функції ---


def item_total(item: Item) -> float:
    """Вартість позиції: ціна × кількість."""
    return float(item["price"]) * int(item["qty"])


def check_total(items: Iterable[Item]) -> float:
    """Сума чека — map позицій у вартості та згортання у суму."""
    return float(sum(map(item_total, items)))


def check_of(order: Order) -> float:
    """Чек замовлення: уже обчислене поле check або сума його позицій."""
    check = order.get("check")
    return check_total(order.get("items", [])) if check is None else float(check)


def make_zone_resolver(
    zones: Mapping[str, range] = DEFAULT_ZONES,
) -> Callable[[int], str]:
    """Фабрика: за номером столика повертає назву зони або "unknown"."""
    return lambda table: next((z for z, r in zones.items() if table in r), "unknown")


zone_of = make_zone_resolver()


# --- чисті трансформації (функції вищого порядку) ---


def with_check() -> Step:
    """map: додати до кожного замовлення поле check (нові словники, вхід без змін)."""
    return lambda orders: (
        {**o, "check": check_total(o.get("items", []))} for o in orders
    )


def boost_zone(
    zone: str, factor: float, resolve: Callable[[int], str] = zone_of
) -> Step:
    """map: застосувати сервісний коефіцієнт до чеків столиків вибраної зони."""

    def _boost(order: Order) -> Order:
        check = check_of(order)
        boosted = check * factor if resolve(order.get("table", 0)) == zone else check
        return {**order, "check": boosted}

    return lambda orders: map(_boost, orders)


def min_check(threshold: float) -> Step:
    """filter: залишити лише чеки не менші за поріг (малі чеки відкидаються)."""
    return lambda orders: filter(lambda o: check_of(o) >= threshold, orders)


def normalize_waiters() -> Step:
    """map: прізвище офіціанта у Title Case без зайвих пробілів."""
    return lambda orders: (
        {**o, "waiter": o.get("waiter", "").strip().title()} for o in orders
    )


def sort_by_check_desc() -> Step:
    """sorted з двома ключами: чек спадно, при рівності — id зростанням."""
    return lambda orders: sorted(orders, key=lambda o: (-check_of(o), o.get("id", 0)))


def take(n: int) -> Step:
    """Top-N через itertools.islice; n <= 0 дає порожній результат."""
    return lambda orders: islice(orders, max(n, 0))


# --- reduce-агрегація ---


def reduce_stats(orders: Iterable[Order]) -> Stats:
    """count, sum_checks, avg_check, max_check одним проходом reduce."""
    count, total, biggest = reduce(
        lambda acc, o: (acc[0] + 1, acc[1] + check_of(o), max(acc[2], check_of(o))),
        orders,
        (0, 0.0, 0.0),
    )
    return {
        "count": count,
        "sum_checks": total,
        "avg_check": total / count if count else 0.0,
        "max_check": biggest,
    }


def revenue_by_waiter(orders: Iterable[Order]) -> dict[str, float]:
    """Виторг кожного офіціанта: reduce будує новий словник на кожному кроці."""
    empty: dict[str, float] = {}
    return reduce(
        lambda acc, o: {**acc, o["waiter"]: acc.get(o["waiter"], 0.0) + check_of(o)},
        orders,
        empty,
    )


# --- складання конвеєра ---


def build_pipeline(
    top_n: int = 3,
    zone: str = "terrace",
    factor: float = 1.1,
    threshold: float = 200.0,
    resolve: Callable[[int], str] = zone_of,
) -> Pipeline:
    """Конвеєр варіанта 4: чек → коефіцієнт зони → фільтр → сортування → Top-N."""
    steps = pipe(
        normalize_waiters(),
        with_check(),
        boost_zone(zone, factor, resolve),
        min_check(threshold),
        sort_by_check_desc(),
        take(top_n),
    )
    return lambda orders: list(steps(orders))


# --- розбір «сирих» даних (наприклад, із JSON) ---


def _as_float(value: object) -> float:
    """Число з JSON-значення; bool і сторонні типи відхиляються."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"not a number: {value!r}")
    return float(value)


def _as_int(value: object) -> int:
    """Ціле з JSON-значення; bool і сторонні типи відхиляються."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"not an integer: {value!r}")
    return int(value)


def parse_item(raw: object) -> Item:
    """Побудувати типізований Item зі словника JSON."""
    if not isinstance(raw, Mapping):
        raise ValueError(f"item must be a mapping: {raw!r}")
    return {
        "name": str(raw.get("name", "")),
        "price": _as_float(raw.get("price", 0)),
        "qty": _as_int(raw.get("qty", 1)),
    }


def parse_order(raw: Mapping[str, object]) -> Order:
    """Побудувати типізований Order зі словника JSON (чисто, без I/O)."""
    items = raw.get("items", [])
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    return {
        "id": _as_int(raw.get("id", 0)),
        "waiter": str(raw.get("waiter", "")),
        "table": _as_int(raw.get("table", 0)),
        "items": [parse_item(it) for it in items],
    }
