#!/usr/bin/env python3
"""CSV と HTML テンプレートから静的サイトを生成する。"""

from __future__ import annotations

import argparse
import csv
import html
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
ARTICLES_DIR = CONTENT_DIR / "articles"
PAGES_DIR = CONTENT_DIR / "pages"
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"
DOCS_ARTICLES_DIR = DOCS_DIR / "articles"
LOGS_DIR = ROOT / "logs"

PRODUCTS_CSV = CONTENT_DIR / "products.csv"
OUTPUT_HTML = DOCS_DIR / "index.html"
ROBOTS_TXT = DOCS_DIR / "robots.txt"
SITEMAP_XML = DOCS_DIR / "sitemap.xml"
BUILD_LOG = LOGS_DIR / "build.log"

SITE_URL = "https://mttakao599.github.io/MiniIncomeLab/"
SITE_TITLE = "MiniIncomeLab | ミニPC比較ガイド"
META_DESCRIPTION = (
    "ミニPC選びの参考情報をまとめた個人運営サイト。"
    "用途別の比較と手動確認した商品情報を掲載しています。"
)
SITE_DESCRIPTION = "ミニPC選びの参考情報を整理する個人運営サイトです。"

PRODUCT_STATUS_ACTIVE = "active"

GENERATED_PATHS: tuple[Path, ...] = (
    OUTPUT_HTML,
    ROBOTS_TXT,
    SITEMAP_XML,
)


@dataclass
class MarkdownDocument:
    slug: str
    title: str
    source: Path
    summary: str


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


def escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def normalize_status(value: str) -> str:
    return (value or PRODUCT_STATUS_ACTIVE).strip().lower()


def filter_active_products(products: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        product
        for product in products
        if normalize_status(product.get("status", "")) == PRODUCT_STATUS_ACTIVE
    ]


def load_products() -> list[dict[str, str]]:
    if not PRODUCTS_CSV.exists():
        raise FileNotFoundError(f"products.csv が見つかりません: {PRODUCTS_CSV}")

    with PRODUCTS_CSV.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if not rows:
        raise ValueError("products.csv に商品データがありません")

    return rows


def parse_markdown_document(path: Path) -> MarkdownDocument:
    text = path.read_text(encoding="utf-8")
    slug = path.stem
    title = slug
    summary = ""

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            continue
        summary = stripped
        break

    return MarkdownDocument(slug=slug, title=title, source=path, summary=summary)


def load_articles() -> list[MarkdownDocument]:
    """記事一覧の並び順: ファイル名（slug）の昇順。"""
    if not ARTICLES_DIR.exists():
        return []

    return [
        parse_markdown_document(path)
        for path in sorted(ARTICLES_DIR.glob("*.md"), key=lambda p: p.stem)
    ]


def load_pages() -> list[MarkdownDocument]:
    """固定ページの並び順: ファイル名（slug）の昇順。"""
    if not PAGES_DIR.exists():
        return []

    return [
        parse_markdown_document(path)
        for path in sorted(PAGES_DIR.glob("*.md"), key=lambda p: p.stem)
    ]


def markdown_to_html(text: str) -> str:
    parts: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            parts.append("</ul>")
            in_list = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            close_list()
            continue

        if stripped.startswith("### "):
            close_list()
            parts.append(f"<h3>{escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_list()
            parts.append(f"<h2>{escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_list()
            parts.append(f"<h1>{escape(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{escape(stripped[2:])}</li>")
        else:
            close_list()
            parts.append(f"<p>{escape(stripped)}</p>")

    close_list()
    return "\n".join(parts)


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


def build_article_list_html(articles: list[MarkdownDocument]) -> str:
    if not articles:
        return "<li>記事は準備中です。</li>"

    items: list[str] = []
    for article in articles:
        href = f"articles/{article.slug}.html"
        items.append(
            f'<li><a href="{href}">{escape(article.title)}</a></li>'
        )
    return "\n".join(items)


def build_html_page(
    *,
    body_template: Path,
    body_values: dict[str, str],
    page_title: str,
    meta_description: str,
    canonical_url: str,
    output_path: Path,
) -> Path:
    page_content = render_template(body_template, body_values)
    final_html = render_template(
        TEMPLATES_DIR / "base.html",
        {
            "page_title": escape(page_title),
            "meta_description": escape(meta_description),
            "canonical_url": escape(canonical_url),
            "og_title": escape(page_title),
            "og_description": escape(meta_description),
            "content": page_content,
        },
    )
    output_path.write_text(final_html, encoding="utf-8")
    return output_path


def build_article_pages(
    articles: list[MarkdownDocument],
    site_updated_date: str,
) -> list[Path]:
    DOCS_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for article in articles:
        markdown = article.source.read_text(encoding="utf-8")
        article_content = markdown_to_html(markdown)
        page_title = f"{article.title} | MiniIncomeLab"
        meta_description = article.summary or META_DESCRIPTION
        canonical_url = f"{SITE_URL}articles/{article.slug}.html"
        output_path = DOCS_ARTICLES_DIR / f"{article.slug}.html"

        written.append(
            build_html_page(
                body_template=TEMPLATES_DIR / "article.html",
                body_values={
                    "article_content": article_content,
                    "site_updated_date": escape(site_updated_date),
                },
                page_title=page_title,
                meta_description=meta_description,
                canonical_url=canonical_url,
                output_path=output_path,
            )
        )

    return written


def build_static_pages(pages: list[MarkdownDocument]) -> list[Path]:
    written: list[Path] = []

    for page in pages:
        markdown = page.source.read_text(encoding="utf-8")
        page_content = markdown_to_html(markdown)
        page_title = f"{page.title} | MiniIncomeLab"
        meta_description = page.summary or META_DESCRIPTION
        canonical_url = f"{SITE_URL}{page.slug}.html"
        output_path = DOCS_DIR / f"{page.slug}.html"

        written.append(
            build_html_page(
                body_template=TEMPLATES_DIR / "page.html",
                body_values={"page_content": page_content},
                page_title=page_title,
                meta_description=meta_description,
                canonical_url=canonical_url,
                output_path=output_path,
            )
        )

    return written


def build_robots_txt() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}sitemap.xml\n"
    )


def build_sitemap_xml(
    lastmod_date: str,
    pages: list[MarkdownDocument],
    articles: list[MarkdownDocument],
) -> str:
    urls = [SITE_URL]
    for page in pages:
        urls.append(f"{SITE_URL}{page.slug}.html")
    for article in articles:
        urls.append(f"{SITE_URL}articles/{article.slug}.html")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{url}</loc>",
                f"    <lastmod>{lastmod_date}</lastmod>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def clean_docs() -> list[Path]:
    removed: list[Path] = []

    for path in GENERATED_PATHS:
        if path.exists():
            path.unlink()
            removed.append(path)

    if DOCS_ARTICLES_DIR.exists():
        for path in DOCS_ARTICLES_DIR.glob("*.html"):
            path.unlink()
            removed.append(path)

    if PAGES_DIR.exists():
        for md_path in PAGES_DIR.glob("*.md"):
            html_path = DOCS_DIR / f"{md_path.stem}.html"
            if html_path.exists():
                html_path.unlink()
                removed.append(html_path)

    return removed


def open_in_browser(html_path: Path) -> None:
    if not html_path.exists():
        raise FileNotFoundError(f"HTML が見つかりません: {html_path}")
    webbrowser.open(html_path.resolve().as_uri())


def build_site(*, clean: bool = False, open_browser: bool = False) -> int:
    build_date = datetime.now().strftime("%Y-%m-%d")
    log("build_site.py 開始")

    try:
        if clean:
            removed = clean_docs()
            if removed:
                names = ", ".join(str(path.relative_to(ROOT)) for path in removed)
                log(f"clean: 削除しました -> {names}")
            else:
                log("clean: 削除対象の生成物はありません")

        products = load_products()
        active_products = filter_active_products(products)
        log(
            f"products.csv を読み込み: {len(products)} 件 "
            f"(表示対象: {len(active_products)} 件)"
        )

        articles = load_articles()
        log(f"articles/*.md を読み込み: {len(articles)} 件")

        pages = load_pages()
        log(f"pages/*.md を読み込み: {len(pages)} 件")

        product_cards = build_product_cards(active_products)
        page_content = render_template(
            TEMPLATES_DIR / "index.html",
            {
                "site_title": escape(SITE_TITLE),
                "site_description": escape(SITE_DESCRIPTION),
                "product_count": escape(str(len(active_products))),
                "site_updated_date": escape(build_date),
                "article_list": build_article_list_html(articles),
                "product_cards": product_cards,
            },
        )

        final_html = render_template(
            TEMPLATES_DIR / "base.html",
            {
                "page_title": escape(SITE_TITLE),
                "meta_description": escape(META_DESCRIPTION),
                "canonical_url": escape(SITE_URL),
                "og_title": escape(SITE_TITLE),
                "og_description": escape(META_DESCRIPTION),
                "content": page_content,
            },
        )

        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "products").mkdir(parents=True, exist_ok=True)
        OUTPUT_HTML.write_text(final_html, encoding="utf-8")

        article_outputs = build_article_pages(articles, build_date)
        for path in article_outputs:
            log(f"生成完了: {path}")

        page_outputs = build_static_pages(pages)
        for path in page_outputs:
            log(f"生成完了: {path}")

        ROBOTS_TXT.write_text(build_robots_txt(), encoding="utf-8")
        SITEMAP_XML.write_text(
            build_sitemap_xml(build_date, pages, articles),
            encoding="utf-8",
        )

        log(f"生成完了: {OUTPUT_HTML}")
        log(f"生成完了: {ROBOTS_TXT}")
        log(f"生成完了: {SITEMAP_XML}")

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
        description="CSV と HTML テンプレートから docs/ 配下の公開ファイルを生成します。",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="再生成前に docs/index.html, docs/about.html, docs/privacy.html, docs/robots.txt, docs/sitemap.xml, docs/articles/*.html を削除する",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="生成後に docs/index.html を既定ブラウザで開く",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    sys.exit(build_site(clean=args.clean, open_browser=args.open))


if __name__ == "__main__":
    main()
