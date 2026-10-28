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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Matrix-1 — izinli platformlarda kontrollü kullanıcı adı denetimi"
    )
    parser.add_argument("username", nargs="?", help="Sorgulanacak kullanıcı adı")
    parser.add_argument("--mode", choices=["single", "multi"], default="multi")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--category", help="Yalnızca bu kategoriye ait platformları kontrol et")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4, help="Eşzamanlı istek sayısı (1-16)")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--delay", type=float, default=0.0, help="İstekler öncesi saniye cinsinden bekleme")
    parser.add_argument("--include-external", action="store_true", help="Kaynak kataloğundaki kapalı harici kayıtları dahil et")
    parser.add_argument("--all-results", action="store_true", help="Bulunamayan ve hatalı sonuçları da yazdır")
    parser.add_argument("--list-platforms", action="store_true", help="Etkin platformları listele ve çık")
    parser.add_argument("--out", default="results.json")
    parser.add_argument("--format", choices=["json", "ndjson", "csv", "txt"], default="json")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit 1 veya daha büyük olmalı")
    if args.workers < 1 or args.workers > 16:
        parser.error("--workers 1 ile 16 arasında olmalı")
    if args.timeout <= 0 or args.delay < 0:
        parser.error("--timeout pozitif, --delay negatif olmayan bir sayı olmalı")
    try:
        catalog = load_catalog(catalog_path(args.catalog), include_external=args.include_external)
        if args.category:
            catalog = [platform for platform in catalog if platform.category.casefold() == args.category.casefold()]
        if args.list_platforms:
            for platform in catalog:
                print(f"{platform.name}\t{platform.category}\t{platform.source}")
            print(f"Toplam platform: {len(catalog)}")
            return
        username = args.username or input("Sorgulanacak kullanıcı adı: ").strip()
        limit = 1 if args.mode == "single" else args.limit
        results = search(
            username,
            catalog,
            limit,
            workers=args.workers,
            timeout=args.timeout,
            delay=args.delay,
            include_inactive=args.all_results,
        )
        export_results(results, args.out, args.format)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Matrix-1 hata: {exc}\n")
    counts: dict[str, int] = {}
    for result in results:
        counts[result.state] = counts.get(result.state, 0) + 1
    summary = ", ".join(f"{state}={count}" for state, count in sorted(counts.items())) or "sonuç yok"
    print(f"Kontrol edilen üst sınır: {limit} | Dönen sonuç: {len(results)} | {summary} | çıktı: {args.out}")


if __name__ == "__main__":
    main()
