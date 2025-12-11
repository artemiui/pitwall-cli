import csv
import json
from pathlib import Path

from source import api, views
from source.cache import F1Cache


def test_fetch_json_returns_cached(monkeypatch, tmp_path):
    """fetch_json should return cached data without issuing HTTP requests."""
    cache = F1Cache(cache_dir=tmp_path / "cache")
    monkeypatch.setattr(api, "f1_cache", cache)

    url = "https://example.com/data"
    cached_payload = {"hello": "world"}
    cache.set(url, cached_payload)

    def _no_session():
        raise AssertionError("requests.Session should not be created on cache hit")

    monkeypatch.setattr(api.requests, "Session", _no_session)

    result = api.fetch_json(url)
    assert result == cached_payload


def test_export_to_csv_flattens_nested_structures(tmp_path):
    """Nested dicts/lists should be flattened and written as CSV columns."""
    data = [
        {"id": 1, "driver": {"name": "Test", "numbers": [1, 2]}},
        {"id": 2, "driver": {"name": "Second", "numbers": [3]}},
    ]

    out_file = tmp_path / "laps.csv"
    views.export_to_csv(data, endpoint="laps", filename=str(out_file))

    with out_file.open() as f:
        rows = list(csv.DictReader(f))

    assert rows[0]["id"] == "1"
    assert rows[0]["driver_name"] == "Test"
    assert rows[0]["driver_numbers"] == "1, 2"
    assert rows[1]["driver_name"] == "Second"


def test_export_data_writes_json_and_builds_url(monkeypatch, tmp_path):
    """export_data should build querystring, fetch, and write JSON file."""
    captured = {}

    def fake_fetch(url, force_refresh=False):
        captured["url"] = url
        return [{"session_key": 123, "driver_number": 44, "value": 1}]

    monkeypatch.setattr(views, "fetch_json", fake_fetch)

    out_file = tmp_path / "out.json"
    views.export_data(
        "laps",
        {"session_key": 123, "driver_number": 44},
        filename=str(out_file),
        format="json",
    )

    with out_file.open() as f:
        payload = json.load(f)

    assert payload[0]["driver_number"] == 44
    assert "session_key=123" in captured["url"]
    assert "driver_number=44" in captured["url"]

