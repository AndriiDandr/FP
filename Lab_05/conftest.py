import pytest


@pytest.fixture
def doubling() -> tuple[float, float]:
    return 1.0, 2.0
