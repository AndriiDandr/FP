"""Корінь лабораторної: pytest додає цей каталог у sys.path; спільна фікстура даних."""

from pathlib import Path

import pytest
from app import load_orders
from core import Order

DATA = Path(__file__).with_name("orders.json")


@pytest.fixture
def orders() -> list[Order]:
    """Дванадцять замовлень із orders.json (той самий файл, що читає app.py)."""
    return load_orders(DATA)
