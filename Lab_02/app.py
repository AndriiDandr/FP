"""Оболонка I/O для ЛР2: аргументи командного рядка, читання JSON, друк результатів.

Уся логіка — у чистих функціях core.py; тут лише читання файлу, розбір аргументів
і форматований вивід. Приклад: python app.py --top 2 --zone vip --factor 1.2
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from core import (
    Order,
    Stats,
    build_pipeline,
    parse_order,
    reduce_stats,
    revenue_by_waiter,
    with_check,
    zone_of,
)

DEFAULT_DATA = Path(__file__).with_name("orders.json")


def load_orders(path: Path) -> list[Order]:
    """Прочитати JSON-файл зі списком замовлень і перетворити записи на Order."""
    with path.open(encoding="utf-8") as src:
        raw = json.load(src)
    if not isinstance(raw, list):
        raise ValueError("orders file must contain a JSON list")
    return [parse_order(item) for item in raw]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Параметри конвеєра: файл даних, Top-N, зона та її коефіцієнт, мінімальний чек."""
    parser = argparse.ArgumentParser(
        description="Варіант 4: рейтинг замовлень ресторану (map/filter/reduce)."
    )
    parser.add_argument(
        "--data", type=Path, default=DEFAULT_DATA, help="JSON із замовленнями"
    )
    parser.add_argument("--top", type=int, default=3, help="скільки чеків показати")
    parser.add_argument(
        "--zone", default="terrace", help="зона із сервісним коефіцієнтом"
    )
    parser.add_argument(
        "--factor", type=float, default=1.1, help="сервісний коефіцієнт"
    )
    parser.add_argument(
        "--min-check", type=float, default=200.0, help="поріг малого чека"
    )
    return parser.parse_args(argv)


def format_order(order: Order) -> str:
    """Рядок таблиці: id, офіціант, столик, зона, сума чека."""
    table = order.get("table", 0)
    return (
        f"#{order.get('id', 0):<2} {order.get('waiter', ''):<8} "
        f"table {table:>2} ({zone_of(table):<7}) check {order.get('check', 0.0):>9.2f}"
    )


def format_stats(stats: Stats) -> str:
    """Рядок підсумку reduce-агрегації."""
    return (
        f"count={stats['count']} sum_checks={stats['sum_checks']:.2f} "
        f"avg_check={stats['avg_check']:.2f} max_check={stats['max_check']:.2f}"
    )


def main(argv: Sequence[str] | None = None) -> None:
    """Прочитати дані, прогнати конвеєр, надрукувати Top-N і агрегати."""
    args = parse_args(argv)
    orders = load_orders(args.data)
    pipeline = build_pipeline(args.top, args.zone, args.factor, args.min_check)
    top = pipeline(orders)

    print(
        f"orders: {len(orders)}, zone '{args.zone}' x{args.factor}, "
        f"min check {args.min_check:.0f}"
    )
    print(f"top-{args.top}:")
    for order in top:
        print("  " + format_order(order))
    print("stats (top):", format_stats(reduce_stats(top)))
    print("stats (all):", format_stats(reduce_stats(with_check()(orders))))
    for waiter, revenue in sorted(
        revenue_by_waiter(top).items(), key=lambda kv: -kv[1]
    ):
        print(f"  {waiter:<8} {revenue:>9.2f}")
    print("input unchanged:", all("check" not in o for o in orders))


if __name__ == "__main__":
    main()
