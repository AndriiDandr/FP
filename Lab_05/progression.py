"""Варіант 4 — геометрична прогресія: лінивий потік q0, q0·r, q0·r², ...

Потік нескінченний, тому всі функції повертають ітератори, а обмеження задається
порогом (takewhile) або кількістю членів (islice). Накопичені сума і добуток
рахуються через itertools.accumulate без матеріалізації потоку.
"""

from __future__ import annotations

import operator
from collections.abc import Iterable, Iterator
from itertools import accumulate, islice, repeat, takewhile
from typing import NamedTuple

MAX_TERMS = 10_000


class ProgressionSummary(NamedTuple):
    """Підсумок членів до порогу: кількість (terms), останній член, сума і добуток."""

    terms: int
    last: float
    total: float
    product: float


def geometric(q0: float, r: float) -> Iterator[float]:
    """Нескінченна геометрична прогресія q0, q0·r, q0·r², ... (власний генератор)."""
    q = q0
    while True:
        yield q
        q *= r


def geometric_accumulate(q0: float, r: float) -> Iterator[float]:
    """Та сама прогресія через accumulate(repeat(r), mul, initial=q0)."""
    return accumulate(repeat(r), operator.mul, initial=q0)


def up_to(
    limit: float, it: Iterable[float], max_terms: int = MAX_TERMS
) -> Iterator[float]:
    """Члени, поки |q| <= limit; max_terms обмежує потік при |r| <= 1."""
    if limit < 0:
        raise ValueError("limit must be >= 0")
    return takewhile(lambda q: abs(q) <= limit, islice(it, max_terms))


def above(
    eps: float, it: Iterable[float], max_terms: int = MAX_TERMS
) -> Iterator[float]:
    """Члени спадної прогресії, поки |q| >= eps (для |r| < 1)."""
    if eps <= 0:
        raise ValueError("eps must be > 0")
    return takewhile(lambda q: abs(q) >= eps, islice(it, max_terms))


def running_sums(it: Iterable[float]) -> Iterator[float]:
    """Накопичені суми S1, S2, ... (accumulate)."""
    return accumulate(it)


def running_products(it: Iterable[float]) -> Iterator[float]:
    """Накопичені добутки P1, P2, ... (accumulate з operator.mul)."""
    return accumulate(it, operator.mul)


def nth_term(q0: float, r: float, n: int) -> float:
    """n-й член за формулою q0·r^n (нумерація з нуля) — для перевірки потоку."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return float(q0 * r**n)


def closed_form_sum(q0: float, r: float, n: int) -> float:
    """Сума перших n членів за формулою q0·(1 - r^n)/(1 - r), або q0·n при r = 1."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if r == 1:
        return float(q0 * n)
    return float(q0 * (1 - r**n) / (1 - r))


def summarize_up_to(
    q0: float, r: float, limit: float, max_terms: int = MAX_TERMS
) -> ProgressionSummary:
    """Один лінивий прохід до порогу: кількість, останній член, сума, добуток."""
    count, last, total, product = 0, 0.0, 0.0, 1.0
    for q in up_to(limit, geometric(q0, r), max_terms):
        count, last, total, product = count + 1, q, total + q, product * q
    return ProgressionSummary(count, last, total, product if count else 0.0)
