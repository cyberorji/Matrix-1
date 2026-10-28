"""Matrix-1: izinli OSINT yardımcıları için güvenli çekirdek."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote
from urllib.request import Request, urlopen

USERNAME = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

@dataclass(frozen=True)
class Platform:
    name: str
    url_template: str
    enabled: bool = True
    official: bool = False
    category: str = "general"

@dataclass(frozen=True)
class Result:
    platform: str
    username: str
    url: str
    active: bool
    status: str


def load_catalog(path: str | Path) -> list[Platform]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    platforms = []
    for item in data:
        if not item.get("enabled", False):
            continue
        if not item.get("official", False):
            continue
        if "{username}" not in item.get("url_template", ""):
            continue
        platforms.append(Platform(**item))
    return platforms


def validate_username(username: str) -> str:
    username = username.strip()
    if not USERNAME.fullmatch(username):
        raise ValueError("Kullanıcı adı 1-64 karakter olmalı; harf, rakam, ., _ veya - içerebilir.")
    return username


def check_platform(platform: Platform, username: str, timeout: float = 8.0) -> Result:
    username = validate_username(username)
    url = platform.url_template.format(username=quote(username, safe=""))
    request = Request(url, headers={"User-Agent": "Matrix-1/1.0 (permissioned-osint)"})
    try:
        with urlopen(request, timeout=timeout) as response:
            # HTTP başarı kodu tek başına hesabın varlığını kanıtlamaz.
            active = 200 <= response.status < 300
            status = f"HTTP {response.status}"
    except Exception as exc:
        active = False
        status = type(exc).__name__
    return Result(platform.name, username, url, active, status)


def search(username: str, catalog: Iterable[Platform], limit: int = 100) -> list[Result]:
    username = validate_username(username)
    results: list[Result] = []
    for platform in list(catalog)[:limit]:
        result = check_platform(platform, username)
        if result.active:  # yalnızca doğrulanabilen aktif sonuçlar dışarı verilir
            results.append(result)
    return results


def export_results(results: Iterable[Result], path: str | Path, fmt: str = "json") -> None:
    rows = [asdict(r) for r in results]
    target = Path(path)
    if fmt == "txt":
        target.write_text("\n".join(f"{r['platform']} | {r['url']} | {r['status']}" for r in rows) + ("\n" if rows else ""), encoding="utf-8")
    elif fmt == "json":
        target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        raise ValueError("Format txt veya json olmalı.")
