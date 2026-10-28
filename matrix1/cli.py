from __future__ import annotations

import argparse
from .core import export_results, load_catalog, search


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Matrix-1 — terminal tabanlı, izinli OSINT yardımcı aracı"
    )
    parser.add_argument("username", nargs="?", help="Sorgulanacak kullanıcı adı")
    parser.add_argument("--mode", choices=["single", "multi"], default="multi", help="Tek platform veya katalogdaki platformlar")
    parser.add_argument("--catalog", default="data/platforms.json")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--out", default="results.json")
    parser.add_argument("--format", choices=["json", "txt"], default="json")
    args = parser.parse_args()

    username = args.username or input("Sorgulanacak kullanıcı adı: ").strip()
    limit = 1 if args.mode == "single" else args.limit
    results = search(username, load_catalog(args.catalog), limit)
    export_results(results, args.out, args.format)
    print(f"Doğrulanabilen aktif sonuç: {len(results)} | çıktı: {args.out}")


if __name__ == "__main__":
    main()
