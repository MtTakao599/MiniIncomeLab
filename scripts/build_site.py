#!/usr/bin/env python3
"""CSV と HTML テンプレートから静的サイトを生成する。"""

from __future__ import annotations

import argparse
import csv
import html
import sys
import webbrowser
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
PUBLIC_DIR = ROOT / "public"
LOGS_DIR = ROOT / "logs"

PRODUCTS_CSV = CONTENT_DIR / "products.csv"
OUTPUT_HTML = PUBLIC_DIR / "index.html"
BUILD_LOG = LOGS_DIR / "build.log"

SITE_TITLE = "MiniIncomeLab | ミニPC比較ガイド"
SITE_DESCRIPTION = (
    "用途別に選べるミニPC比較サイト（v0.1）。"
    "商品情報は手動管理のサンプルデータです。"
)

# 再生成前に削除する生成物。将来 HTML を増やしたらここに追加する。
GENERATED_PATHS: tuple[Path, ...] = (
    OUTPUT_HTML,
)


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with BUILD_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def render_template(template_path: Path, values: dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace(f"{{{{ {key} }}}}", value)
    return content


def load_products() -> list[dict[str, str]]:
    if not PRODUCTS_CSV.exists():
        raise FileNotFoundError(f"products.csv が見つかりません: {PRODUCTS_CSV}")

    with PRODUCTS_CSV.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        raise ValueError("products.csv に商品データがありません")

    return rows


def escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def build_product_cards(products: list[dict[str, str]]) -> str:
    card_template = TEMPLATES_DIR / "product_card.html"
    cards: list[str] = []

    for product in products:
        cards.append(
            render_template(
                card_template,
                {
                    "name": escape(product.get("name", "")),
                    "category": escape(product.get("category", "")),
                    "cpu": escape(product.get("cpu", "")),
                    "memory": escape(product.get("memory", "")),
                    "storage": escape(product.get("storage", "")),
                    "os": escape(product.get("os", "")),
                    "use_case": escape(product.get("use_case", "")),
                    "pros": escape(product.get("pros", "")),
                    "cons": escape(product.get("cons", "")),
                    "rating": escape(product.get("rating", "")),
                    "amazon_url": escape(product.get("amazon_url", "")),
                    "rakuten_url": escape(product.get("rakuten_url", "")),
                    "last_checked": escape(product.get("last_checked", "")),
                },
            )
        )

    return "\n".join(cards)


def clean_public() -> list[Path]:
    removed: list[Path] = []
    for path in GENERATED_PATHS:
        if path.exists():
            path.unlink()
            removed.append(path)
    return removed


def open_in_browser(html_path: Path) -> None:
    if not html_path.exists():
        raise FileNotFoundError(f"HTML が見つかりません: {html_path}")
    webbrowser.open(html_path.resolve().as_uri())


def build_site(*, clean: bool = False, open_browser: bool = False) -> int:
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("build_site.py 開始")

    try:
        if clean:
            removed = clean_public()
            if removed:
                names = ", ".join(str(path.relative_to(ROOT)) for path in removed)
                log(f"clean: 削除しました -> {names}")
            else:
                log("clean: 削除対象の生成物はありません")

        products = load_products()
        log(f"products.csv を読み込み: {len(products)} 件")

        product_cards = build_product_cards(products)
        page_content = render_template(
            TEMPLATES_DIR / "index.html",
            {
                "site_title": escape(SITE_TITLE),
                "site_description": escape(SITE_DESCRIPTION),
                "product_count": escape(str(len(products))),
                "build_time": escape(build_time),
                "product_cards": product_cards,
            },
        )

        final_html = render_template(
            TEMPLATES_DIR / "base.html",
            {
                "page_title": escape(SITE_TITLE),
                "content": page_content,
            },
        )

        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        (PUBLIC_DIR / "products").mkdir(parents=True, exist_ok=True)
        OUTPUT_HTML.write_text(final_html, encoding="utf-8")

        log(f"生成完了: {OUTPUT_HTML}")

        if open_browser:
            open_in_browser(OUTPUT_HTML)
            log(f"ブラウザで開きました: {OUTPUT_HTML}")

        log("build_site.py 正常終了")
        return 0
    except Exception as exc:
        log(f"ERROR: {exc}")
        return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CSV と HTML テンプレートから public/index.html を生成します。",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="再生成前に public/ 内の既知の生成物（現状は index.html）を削除する",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="生成後に public/index.html を既定ブラウザで開く",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    sys.exit(build_site(clean=args.clean, open_browser=args.open))


if __name__ == "__main__":
    main()
