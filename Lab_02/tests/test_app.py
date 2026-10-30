import json
from pathlib import Path

import pytest
from app import DEFAULT_DATA, format_order, format_stats, load_orders, main, parse_args


def test_default_data_exists_and_loads() -> None:
    orders = load_orders(DEFAULT_DATA)
    assert len(orders) == 12
    assert orders[0] == {
        "id": 1,
        "waiter": "olena",
        "table": 3,
        "items": [
            {"name": "борщ", "price": 95.0, "qty": 2},
            {"name": "хліб", "price": 20.0, "qty": 1},
        ],
    }


def test_load_orders_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"id": 1}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_orders(path)


def test_parse_args_defaults_and_overrides() -> None:
    args = parse_args([])
    assert (args.top, args.zone, args.factor, args.min_check) == (
        3,
        "terrace",
        1.1,
        200.0,
    )
    assert args.data == DEFAULT_DATA
    custom = parse_args(
        ["--top", "2", "--zone", "vip", "--factor", "1.5", "--min-check", "0"]
    )
    assert (custom.top, custom.zone, custom.factor, custom.min_check) == (
        2,
        "vip",
        1.5,
        0.0,
    )


def test_format_helpers() -> None:
    line = format_order({"id": 2, "waiter": "Taras", "table": 12, "check": 858.0})
    assert line.startswith("#2") and "terrace" in line and line.endswith("858.00")
    assert format_stats(
        {"count": 2, "sum_checks": 3.0, "avg_check": 1.5, "max_check": 2.0}
    ) == ("count=2 sum_checks=3.00 avg_check=1.50 max_check=2.00")


def test_main_prints_top_and_stats(capsys: pytest.CaptureFixture[str]) -> None:
    main(["--top", "2"])
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert lines[0] == "orders: 12, zone 'terrace' x1.1, min check 200"
    assert lines[1] == "top-2:"
    assert lines[2].startswith("  #8  Bohdan") and lines[2].endswith("1300.00")
    assert lines[3].startswith("  #5  Olena") and lines[3].endswith("1200.00")
    assert (
        "stats (top): count=2 sum_checks=2500.00 avg_check=1250.00 max_check=1300.00"
        in out
    )
    assert out.rstrip().endswith("input unchanged: True")


def test_main_with_custom_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "orders.json"
    path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "waiter": "a",
                    "table": 1,
                    "items": [{"name": "x", "price": 10, "qty": 1}],
                },
                {
                    "id": 2,
                    "waiter": "b",
                    "table": 1,
                    "items": [{"name": "y", "price": 50, "qty": 1}],
                },
            ]
        ),
        encoding="utf-8",
    )
    main(["--data", str(path), "--min-check", "30", "--zone", "hall", "--factor", "2"])
    out = capsys.readouterr().out
    assert "orders: 2" in out
    assert "#2  B" in out and "100.00" in out
    assert "#1 " not in out
