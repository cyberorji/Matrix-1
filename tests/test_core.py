import json
from pathlib import Path

import pytest

from matrix1.core import Detection, Platform, Result, export_results, load_catalog, search, validate_username


def test_catalog_filters_disabled_and_external_by_default(tmp_path: Path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps([
        {"name": "ok", "url_template": "https://example.com/{username}", "enabled": True, "official": True},
        {"name": "off", "url_template": "https://example.com/{username}", "enabled": False, "official": True},
        {"name": "external", "url_template": "https://example.org/{username}", "enabled": False, "official": False, "source": "WhatsMyName"},
    ]), encoding="utf-8")
    assert [item.name for item in load_catalog(path)] == ["ok"]
    assert [item.name for item in load_catalog(path, include_external=True)] == ["ok", "external"]


def test_catalog_rejects_invalid_template(tmp_path: Path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps([{"name": "broken", "url_template": "ftp://example.com/user"}]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_catalog(path)


def test_username_validation():
    assert validate_username("alice_01") == "alice_01"
    for value in ["", "a/b", "x" * 65]:
        with pytest.raises(ValueError):
            validate_username(value)


def test_classification_and_backward_compatible_active_property():
    result = Result("GitHub", "alice", "https://github.com/alice", "found", "HTTP 200")
    assert result.active is True
    assert Result("GitHub", "alice", "https://github.com/alice", "unknown", "HTTP 200").active is False


def test_export_formats(tmp_path: Path):
    results = [Result("GitHub", "alice", "https://github.com/alice", "found", "HTTP 200")]
    for fmt, suffix in [("json", "json"), ("ndjson", "ndjson"), ("csv", "csv"), ("txt", "txt")]:
        out = tmp_path / f"result.{suffix}"
        export_results(results, out, fmt)
        assert out.exists()
        assert "GitHub" in out.read_text(encoding="utf-8")


def test_search_preserves_order_and_supports_inactive(monkeypatch):
    platforms = [
        Platform("A", "https://example.com/{username}", detection=Detection(found_status=200)),
        Platform("B", "https://example.org/{username}", detection=Detection(found_status=200)),
    ]

    def fake_check(platform, username, timeout=8.0, delay=0.0):
        state = "found" if platform.name == "A" else "unknown"
        return Result(platform.name, username, platform.url_template, state, "HTTP 200")

    monkeypatch.setattr("matrix1.core.check_platform", fake_check)
    assert [r.platform for r in search("alice", platforms)] == ["A"]
    assert [r.platform for r in search("alice", platforms, include_inactive=True)] == ["A", "B"]
