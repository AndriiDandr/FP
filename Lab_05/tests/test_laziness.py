from collections.abc import Iterator
from itertools import islice

from progression import running_sums, up_to
from streams import drop, moving_average, sliding_window, take


class CountingSource:
    """Ітератор, що рахує, скільки елементів у нього реально запитали."""

    def __init__(self) -> None:
        self.pulled = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        self.pulled += 1
        return self.pulled


class CountingGeometric:
    """Геометрична прогресія, що рахує кожен згенерований член."""

    def __init__(self, q0: float, r: float) -> None:
        self.q, self.r, self.pulled = q0, r, 0

    def __iter__(self) -> Iterator[float]:
        return self

    def __next__(self) -> float:
        self.pulled += 1
        q, self.q = self.q, self.q * self.r
        return q


def test_take_pulls_exactly_n() -> None:
    src = CountingSource()
    assert take(4, src) == [1, 2, 3, 4]
    assert src.pulled == 4


def test_sliding_window_pulls_only_what_is_consumed() -> None:
    src = CountingSource()
    windows = sliding_window(src, 3)
    assert src.pulled == 0
    assert next(windows) == (1, 2, 3)
    assert src.pulled == 3
    assert next(windows) == (2, 3, 4)
    assert src.pulled == 4


def test_pipeline_is_lazy_end_to_end() -> None:
    src = CountingSource()
    pipeline = moving_average(drop(2, src), 2)
    assert src.pulled == 2
    assert list(islice(pipeline, 2)) == [3.5, 4.5]
    assert src.pulled == 5


def test_up_to_stops_at_first_term_over_limit() -> None:
    src = CountingGeometric(1, 2)
    terms = up_to(100, src)
    assert src.pulled == 0
    assert list(terms) == [1, 2, 4, 8, 16, 32, 64]
    assert src.pulled == 8


def test_running_sums_are_lazy() -> None:
    src = CountingGeometric(3, 2)
    sums = running_sums(src)
    assert src.pulled == 0
    assert take(3, sums) == [3, 9, 21]
    assert src.pulled == 3
