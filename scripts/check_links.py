#!/usr/bin/env python3
"""products.csv 内のアフィリエイトリンクを簡易チェックする。"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_CSV = ROOT / "content" / "products.csv"

LINK_COLUMNS = ("amazon_url", "rakuten_url")
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def looks_like_url(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if not URL_PATTERN.match(value):
        return False
    parsed = urlparse(value)
    return bool(parsed.netloc)


def check_links() -> int:
    if not PRODUCTS_CSV.exists():
        print(f"ERROR: products.csv が見つかりません: {PRODUCTS_CSV}")
        return 1

    errors: list[str] = []

    with PRODUCTS_CSV.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row_num, row in enumerate(reader, start=2):
            product_id = row.get("id", "").strip() or f"row-{row_num}"
            product_name = row.get("name", "").strip() or "(名称なし)"

            for column in LINK_COLUMNS:
                value = (row.get(column) or "").strip()
                if not value:
                    errors.append(
                        f"行 {row_num} [{product_id}] {product_name}: "
                        f"{column} が空です"
                    )
                elif not looks_like_url(value):
                    errors.append(
                        f"行 {row_num} [{product_id}] {product_name}: "
                        f"{column} が URL 形式ではありません -> {value}"
                    )

    if errors:
        print("リンクチェック: NG")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("リンクチェック: OK（全リンクが空でなく、URL形式です）")
    return 0


def main() -> None:
    sys.exit(check_links())


if __name__ == "__main__":
    main()
