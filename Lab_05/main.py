"""Демо ЛР5: нескінченні потоки, вікна та геометрична прогресія (варіант 4)."""

from __future__ import annotations

from progression import (
    above,
    closed_form_sum,
    geometric,
    geometric_accumulate,
    running_products,
    running_sums,
    summarize_up_to,
    up_to,
)
from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    prefix_sums,
    take,
    window_sums,
)


def main() -> None:
    """Друкує приклади роботи потоків (єдиний I/O у лабораторній)."""
    print("fib first 10:", take(10, fib_stream()))
    print("fib drop 5 take 8:", take(8, drop(5, fib_stream())))
    print(
        "window sums of naturals (k=3, first 10):", take(10, window_sums(naturals(), 3))
    )
    print("moving average [1..6], k=2:", list(moving_average([1, 2, 3, 4, 5, 6], 2)))
    print("prefix sums [1,2,3,4]:", list(prefix_sums([1, 2, 3, 4])))

    print("geometric q0=3, r=2, first 8:", take(8, geometric(3, 2)))
    print("via accumulate, first 8:      ", take(8, geometric_accumulate(3, 2)))
    print("terms <= 1000:", list(up_to(1000, geometric(3, 2))))
    print("running sums:", list(running_sums(up_to(1000, geometric(3, 2)))))
    print("running products (first 5):", take(5, running_products(geometric(3, 2))))
    print("decaying q0=1, r=0.5, |q| >= 0.01:", list(above(0.01, geometric(1, 0.5))))
    print("closed form S8:", closed_form_sum(3, 2, 8))
    summary = summarize_up_to(3, 2, 1000)
    print(
        f"summary <= 1000: terms={summary.terms} last={summary.last:g} "
        f"total={summary.total:g} product={summary.product:g}"
    )


if __name__ == "__main__":
    main()
