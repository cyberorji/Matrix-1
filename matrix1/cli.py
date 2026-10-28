from __future__ import annotations
import argparse
from .core import load_catalog, search, export_results

def main() -> None:
    p = argparse.ArgumentParser(description="Matrix-1 güvenli, izinli OSINT yardımcı aracı")
    p.add_argument("username", help="Sorgulanacak kullanıcı adı")
    p.add_argument("--catalog", default="data/platforms.json")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--out", default="results.json")
    p.add_argument("--format", choices=["json", "txt"], default="json")
    args = p.parse_args()
    results = search(args.username, load_catalog(args.catalog), args.limit)
    export_results(results, args.out, args.format)
    print(f"Doğrulanabilen aktif sonuç: {len(results)} | çıktı: {args.out}")

if __name__ == "__main__":
    main()
