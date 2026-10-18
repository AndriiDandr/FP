import pytest
from model import Product, StockRecord, make_record


@pytest.fixture
def record() -> StockRecord:
    return make_record(
        1,
        Product("LAP-01", "Laptop", 1_000.0),
        (4, 6),
        frozenset({"new"}),
        name="TechImport",
        city="Kyiv",
    )
