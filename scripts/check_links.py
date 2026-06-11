#!/usr/bin/env python3
"""affiliate_links.csv 内のアフィリエイトリンクを簡易チェックする。"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_SOURCE_CSV = ROOT / "content" / "products_source.csv"
AFFILIATE_LINKS_CSV = ROOT / "content" / "affiliate_links.csv"

LINK_COLUMNS = ("amazon_url", "rakuten_url")
PRODUCT_STATUS_ACTIVE = "active"
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


def looks_like_url(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if not URL_PATTERN.match(value):
        return False
    parsed = urlparse(value)
    return bool(parsed.netloc)


def normalize_status(value: str) -> str:
    return (value or PRODUCT_STATUS_ACTIVE).strip().lower()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load_products_source() -> list[dict[str, str]]:
    if not PRODUCTS_SOURCE_CSV.exists():
        print(f"ERROR: products_source.csv が見つかりません: {PRODUCTS_SOURCE_CSV}")
        sys.exit(1)
    return read_csv_rows(PRODUCTS_SOURCE_CSV)


def load_affiliate_links() -> list[dict[str, str]]:
    if not AFFILIATE_LINKS_CSV.exists():
        print(f"ERROR: affiliate_links.csv が見つかりません: {AFFILIATE_LINKS_CSV}")
        sys.exit(1)
    return read_csv_rows(AFFILIATE_LINKS_CSV)


def check_links() -> int:
    products = load_products_source()
    affiliate_rows = load_affiliate_links()

    product_ids = {
        (row.get("id") or "").strip()
        for row in products
        if (row.get("id") or "").strip()
    }
    active_product_ids = {
        (row.get("id") or "").strip()
        for row in products
        if (row.get("id") or "").strip()
        and normalize_status(row.get("status", "")) == PRODUCT_STATUS_ACTIVE
    }
    affiliate_ids = {
        (row.get("id") or "").strip()
        for row in affiliate_rows
        if (row.get("id") or "").strip()
    }

    errors: list[str] = []
    warnings: list[str] = []

    for product_id in sorted(active_product_ids - affiliate_ids):
        warnings.append(
            f"[{product_id}] active 商品ですが affiliate_links.csv に行がありません"
        )

    for product_id in sorted(affiliate_ids - product_ids):
        warnings.append(
            f"[{product_id}] affiliate_links.csv にありますが "
            "products_source.csv に存在しません"
        )

    for row_num, row in enumerate(affiliate_rows, start=2):
        product_id = (row.get("id") or "").strip() or f"row-{row_num}"

        for column in LINK_COLUMNS:
            value = (row.get(column) or "").strip()
            if not value:
                continue
            if not looks_like_url(value):
                errors.append(
                    f"affiliate_links.csv 行 {row_num} [{product_id}]: "
                    f"{column} が URL 形式ではありません -> {value}"
                )

    if warnings:
        print("リンクチェック: 警告あり")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("リンクチェック: NG")
        for error in errors:
            print(f"  - {error}")
        return 1

    if warnings:
        print(
            "リンクチェック: OK"
            "（空欄は許容。不正 URL のみエラー。警告あり）"
        )
    else:
        print(
            "リンクチェック: OK"
            "（affiliate_links.csv を確認。空欄は許容、不正 URL のみエラー）"
        )
    return 0


def main() -> None:
    sys.exit(check_links())


if __name__ == "__main__":
    main()
