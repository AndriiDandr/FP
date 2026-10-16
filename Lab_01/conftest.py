"""Спільні фікстури для тестів."""

import pytest

from core import Item


@pytest.fixture
def sample_cart() -> list[Item]:
    """Тестовий кошик: три звичайні товари і один з нульовою кількістю."""
    return [
        {"name": "Phone", "price": 1000.0, "qty": 1, "category": "electronics"},
        {"name": "Book", "price": 200.0, "qty": 2, "category": "books"},
        {"name": "Bread", "price": 30.0, "qty": 5, "category": "food"},
        {"name": "Ghost", "price": 99.0, "qty": 0, "category": "books"},
    ]
