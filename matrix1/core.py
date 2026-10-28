"""Matrix-1: izinli platformlarda kullanıcı adı varlığını kontrollü biçimde denetler."""
from __future__ import annotations

import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

USERNAME = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
ALLOWED_SCHEMES = {"http", "https"}
MAX_BODY_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class Detection:
    found_status: int | None = None
    found_text: str = ""
    missing_status: int | None = None
    missing_text: str = ""


@dataclass(frozen=True)
class Platform:
    name: str
    url_template: str
    enabled: bool = True
    official: bool = False
    category: str = "general"
    source: str = "Matrix-1"
    source_license: str = ""
    detection: Detection = field(default_factory=Detection)


@dataclass(frozen=True)
class Result:
    platform: str
    username: str
    url: str
    state: str
    status: str
    matched: str = ""
    category: str = "general"
    source: str = "Matrix-1"

    @property
    def active(self) -> bool:
        """Backward-compatible alias for callers using the old API."""
        return self.state == "found"


def _as_optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("HTTP durum kodları sayı olmalı.") from exc
    if not 100 <= parsed <= 599:
        raise ValueError("HTTP durum kodları 100 ile 599 arasında olmalı.")
    return parsed


def _parse_detection(item: Mapping[str, object]) -> Detection:
    raw = item.get("detection", {}) or {}
    if not isinstance(raw, Mapping):
        raise ValueError("detection alanı nesne olmalı.")
    return Detection(
        found_status=_as_optional_int(raw.get("found_status")),
        found_text=str(raw.get("found_text", "") or ""),
        missing_status=_as_optional_int(raw.get("missing_status")),
        missing_text=str(raw.get("missing_text", "") or ""),
    )


def _validate_platform(item: Mapping[str, object]) -> Platform:
    required = ("name", "url_template")
    missing = [key for key in required if not str(item.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Platform alanları eksik: {', '.join(missing)}")
    name = str(item["name"]).strip()
    template = str(item["url_template"]).strip()
    if "{username}" not in template:
        raise ValueError(f"{name}: url_template {{username}} içermeli.")
    probe = template.replace("{username}", "probe-user")
    parsed = urlparse(probe)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ValueError(f"{name}: yalnızca geçerli http/https URL kullanılabilir.")
    return Platform(
        name=name,
        url_template=template,
        enabled=bool(item.get("enabled", False)),
        official=bool(item.get("official", False)),
        category=str(item.get("category", "general") or "general"),
        source=str(item.get("source", "Matrix-1") or "Matrix-1"),
        source_license=str(item.get("source_license", "") or ""),
        detection=_parse_detection(item),
    )


def load_catalog(path: str | Path, *, include_external: bool = False) -> list[Platform]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Katalog kök seviyede JSON listesi olmalı.")
    platforms: list[Platform] = []
    names: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("Katalogdaki her kayıt nesne olmalı.")
        platform = _validate_platform(item)
        is_external = bool(platform.source and platform.source != "Matrix-1")
        if not platform.enabled and not (include_external and is_external):
            continue
        if not platform.official and not include_external:
            continue
        key = platform.name.casefold()
        if key in names:
            raise ValueError(f"Tekrarlanan platform adı: {platform.name}")
        names.add(key)
        platforms.append(platform)
    return platforms


def validate_username(username: str) -> str:
    username = username.strip()
    if not USERNAME.fullmatch(username):
        raise ValueError("Kullanıcı adı 1-64 karakter olmalı; harf, rakam, ., _ veya - içerebilir.")
    return username


def _classify(response_status: int, body: str, detection: Detection) -> tuple[str, str]:
    body_lower = body.casefold()
    if detection.missing_status == response_status and (
        not detection.missing_text or detection.missing_text.casefold() in body_lower
    ):
        return "not_found", "missing-marker"
    if detection.found_status == response_status and (
        not detection.found_text or detection.found_text.casefold() in body_lower
    ):
        return "found", "found-marker"
    if response_status == 429:
        return "rate_limited", "http-429"
    if 200 <= response_status < 400:
        return "unknown", "ambiguous-success"
    if response_status in (401, 403):
        return "blocked", f"http-{response_status}"
    if response_status == 404:
        return "not_found", "http-404"
    if response_status >= 500:
        return "server_error", f"http-{response_status}"
    return "unknown", f"http-{response_status}"


def check_platform(
    platform: Platform,
    username: str,
    timeout: float = 8.0,
    delay: float = 0.0,
) -> Result:
    username = validate_username(username)
    if delay > 0:
        time.sleep(delay)
    url = platform.url_template.format(username=quote(username, safe=""))
    request = Request(url, headers={
        "User-Agent": "Matrix-1/1.1 (+https://github.com/cyberorji/Matrix-1; permissioned-osint)",
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.1",
    })
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(MAX_BODY_BYTES).decode("utf-8", errors="replace")
            state, matched = _classify(response.status, body, platform.detection)
            status = f"HTTP {response.status}"
    except HTTPError as exc:
        state, matched = _classify(exc.code, "", platform.detection)
        status = f"HTTP {exc.code}"
    except (TimeoutError, URLError, OSError) as exc:
        state, matched = "network_error", type(exc).__name__
        status = type(exc).__name__
    return Result(platform.name, username, url, state, status, matched, platform.category, platform.source)


def search(
    username: str,
    catalog: Iterable[Platform],
    limit: int = 100,
    *,
    workers: int = 4,
    timeout: float = 8.0,
    delay: float = 0.0,
    include_inactive: bool = False,
) -> list[Result]:
    username = validate_username(username)
    if limit < 1:
        raise ValueError("limit 1 veya daha büyük olmalı.")
    if not 1 <= workers <= 16:
        raise ValueError("workers 1 ile 16 arasında olmalı.")
    if timeout <= 0 or delay < 0:
        raise ValueError("timeout pozitif, delay ise negatif olmayan bir sayı olmalı.")
    platforms = list(catalog)[:limit]
    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(platforms) or 1)) as pool:
        futures = {
            pool.submit(check_platform, platform, username, timeout, delay): index
            for index, platform in enumerate(platforms)
        }
        ordered: dict[int, Result] = {}
        for future in as_completed(futures):
            ordered[futures[future]] = future.result()
    for index in sorted(ordered):
        result = ordered[index]
        if include_inactive or result.active:
            results.append(result)
    return results


def export_results(results: Iterable[Result], path: str | Path, fmt: str = "json") -> None:
    rows = [asdict(result) for result in results]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "txt":
        target.write_text(
            "".join(f"{r['platform']} | {r['state']} | {r['url']} | {r['status']}\n" for r in rows),
            encoding="utf-8",
        )
    elif fmt == "json":
        target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif fmt == "ndjson":
        target.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    elif fmt == "csv":
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(Result.__dataclass_fields__))
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError("Format json, ndjson, csv veya txt olmalı.")
