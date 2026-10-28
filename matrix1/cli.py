from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import export_results, load_catalog, search


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = PROJECT_ROOT / "data" / "platforms.json"


def catalog_path(value: str) -> str:
    """Use an explicit path, or locate the clone's data folder reliably."""
    if value != str(DEFAULT_CATALOG):
        return value
    candidates = (DEFAULT_CATALOG, Path.cwd() / "data" / "platforms.json")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return str(DEFAULT_CATALOG)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Matrix-1 — terminal tabanlı, izinli OSINT yardımcı aracı"
    )
    parser.add_argument("username", nargs="?", help="Sorgulanacak kullanıcı adı")
    parser.add_argument("--mode", choices=["single", "multi"], default="multi")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--out", default="results.json")
    parser.add_argument("--format", choices=["json", "txt"], default="json")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit 1 veya daha büyük olmalı")
    username = args.username or input("Sorgulanacak kullanıcı adı: ").strip()
    limit = 1 if args.mode == "single" else args.limit
    try:
        catalog = load_catalog(catalog_path(args.catalog))
        results = search(username, catalog, limit)
        export_results(results, args.out, args.format)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Matrix-1 hata: {exc}\n")
    print(f"Doğrulanabilen aktif sonuç: {len(results)} | çıktı: {args.out}")


if __name__ == "__main__":
    main()
