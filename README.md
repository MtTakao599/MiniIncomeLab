# MiniIncomeLab

ミニPC上の Ubuntu で定期実行し、静的サイトを自動生成するアフィリエイト/情報サイト生成ツール（v0.1.4）。

- **開発**: Windows + Cursor
- **管理**: GitHub
- **生成**: Python + CSV + HTML テンプレート（標準ライブラリのみ）
- **公開**: GitHub Pages または Cloudflare Pages（`docs/` をそのまま公開）
- **実行環境**: ミニPC（Ubuntu、外部公開なし）

## プロジェクト概要

MiniIncomeLab は、商品情報を `content/products.csv` に手動で書き込み、`scripts/build_site.py` で静的 HTML を生成する最小構成のサイトビルダーです。

v0.1.4 では「ミニPC比較サイト」の一覧ページ（`docs/index.html`）、記事ページ（`docs/articles/*.html`）、固定ページ（`docs/about.html` / `docs/privacy.html`）、SEO 最低限整備（meta / robots.txt / sitemap.xml）を対象としています。将来的には中古PC、Linux、タイ移住準備、管理人便利グッズなどへ横展開できるよう、CSV + テンプレート + Markdown 構成を維持します。

**v0.1.4 時点では、商品情報とリンク先 URL はすべて手動管理です。** 価格・在庫・仕様の自動取得は行いません。Amazonアソシエイト / 楽天アフィリエイトには未参加です。

### Amazon 申請前の方針

Amazonアソシエイト申請前に、**10 記事程度のオリジナルコンテンツ**を `content/articles/` に用意する方針です。v0.1.3 で記事 10 本を整備済みです。v0.1.4 では **アフィリエイト申請前の信頼性整備**として、運営者情報ページとプライバシーポリシーページを追加しています。

### 方針

- CMS や DB は使わない
- 外部サイトのスクレイピングはしない
- 価格の自動取得もしない
- 商品情報・アフィリエイトリンクは CSV を手動更新する
- ミニPCは cron 実行専用とし、外部公開しない
- 生成物（`docs/`）のみ GitHub Pages / Cloudflare Pages で公開する

## v0.1 ではやらないこと

- 価格の自動取得
- 外部サイトのスクレイピング
- データベース（DB）の利用
- CMS の導入
- ミニPCの外部公開（Web サーバー常駐など）
- 自動デプロイ CI（v0.2 以降で検討）
- 商品ページの個別 HTML 生成（`docs/products/` は将来用）

## ディレクトリ構成

```
MiniIncomeLab/
  content/
    products.csv          # 商品データ（手動更新）
    articles/             # 記事 Markdown（*.md）
    pages/                # 固定ページ Markdown（about.md, privacy.md 等）
  templates/
    base.html             # 共通レイアウト + CSS
    index.html            # トップページ
    article.html          # 記事ページ
    page.html             # 固定ページ
    product_card.html     # 商品カード
  scripts/
    build_site.py         # サイト生成
    check_links.py        # リンク簡易チェック
  docs/                   # 生成された静的ファイル（公開ディレクトリ）
    index.html
    about.html            # 運営者情報（生成物）
    privacy.html          # プライバシーポリシー（生成物）
    robots.txt
    sitemap.xml
    articles/             # 記事 HTML（生成物）
    .nojekyll
    products/             # 将来の個別ページ用
  logs/                   # ビルドログ（*.log は Git 管理外）
```

## 必要環境

- Python 3.10 以上（3.12 推奨）
- 追加 pip パッケージは不要（標準ライブラリのみ）

## 初回動作確認チェックリスト

Windows で clone または作成直後に、以下を順に確認してください。

- [ ] `python --version` で Python 3.10 以上が表示される
- [ ] `python scripts\check_links.py` が `リンクチェック: OK` で終了する（終了コード 0）
- [ ] `python scripts\build_site.py --clean --open` で `docs\index.html` が生成され、ブラウザが開く
- [ ] ブラウザで商品カードが 3 件表示される
- [ ] ページ下部にアフィリエイト表記がある
- [ ] スマホ幅（DevTools 等）で 1 列レイアウトになる
- [ ] `logs\build.log` が作成され、再実行で追記される
- [ ] `logs\build.log` と `logs\cron.log` が Git に含まれない（`.gitignore` 確認）
- [ ] `docs\about.html` と `docs\privacy.html` が生成される
- [ ] `docs\sitemap.xml` にトップページ、固定ページ 2 件、記事 URL が含まれる
- [ ] `docs\index.html`、`docs\about.html`、`docs\privacy.html`、`docs\robots.txt`、`docs\sitemap.xml`、`docs\articles\*.html`、`docs\.nojekyll` が Git のコミット対象になる

Ubuntu ミニPC では `\` を `/` に読み替えて同様に確認します。

## Windows での実行方法

PowerShell またはコマンドプロンプトでプロジェクト直下に移動し、以下を実行します。

```powershell
cd D:\dev\MiniIncomeLab
python scripts\check_links.py
python scripts\build_site.py --clean --open
```

手動で HTML を確認する場合:

```powershell
start docs\index.html
```

オプション:

| オプション | 説明 |
|-----------|------|
| `--clean` | 再生成前に `docs/index.html`、`docs/about.html`、`docs/privacy.html`、`docs/robots.txt`、`docs/sitemap.xml`、`docs/articles/*.html` を削除 |
| `--open` | 生成後に既定ブラウザで `docs/index.html` を開く |

ビルド結果は `logs\build.log` に記録されます（追記方式）。

## Ubuntu での実行方法

```bash
cd /home/koishi/MiniIncomeLab
python3 scripts/check_links.py
python3 scripts/build_site.py --clean
```

生成物は `docs/index.html`、`docs/about.html`、`docs/privacy.html`、`docs/articles/*.html`、`docs/robots.txt`、`docs/sitemap.xml` です。パスは `pathlib.Path` を使っているため、Windows / Linux どちらでも同じスクリプトが動きます。

- 記事: `content/articles/*.md` → `docs/articles/<slug>.html`
- 固定ページ: `content/pages/*.md` → `docs/<slug>.html`

対応 Markdown 記法は見出し（`#` / `##` / `###`）、段落、箇条書き（`-`）のみです。

## cron で毎日 4 時に実行する例

ミニPC（Ubuntu）で crontab を編集します。

```bash
crontab -e
```

以下を追加します。

```cron
0 4 * * * cd /home/koishi/MiniIncomeLab && /usr/bin/python3 scripts/build_site.py --clean >> logs/cron.log 2>&1
```

必要に応じて、実行前に `git pull` や `check_links.py` を追加してください。

## 公開方法（GitHub Pages / Cloudflare Pages）

`docs/` 配下がそのまま公開ディレクトリになります。ビルド後の `docs/index.html` がサイトのトップページです。

### GitHub Pages

1. リポジトリ **Settings** → **Pages**
2. **Build and deployment** → Source: **Deploy from a branch**
3. Branch: **`main`**、Folder: **`/docs`**
4. ミニPC でビルド → `docs/` を commit / push

`docs/.nojekyll` により Jekyll 処理を無効化し、静的 HTML をそのまま配信します。

### Cloudflare Pages

1. プロジェクト作成時に Git リポジトリを接続
2. **Build command**: 空（または `python3 scripts/build_site.py`）
3. **Build output directory**: `docs`
4. リポジトリに生成済み `docs/` を含める運用でも、Cloudflare 上でビルドする運用でも可

ミニPC自体はルーター越しに外部公開せず、生成と Git 同期のみ行う想定です。

## 商品情報の更新

1. `content/products.csv` を編集する
2. `python scripts/check_links.py` でリンクを確認する
3. `python scripts/build_site.py --clean` で再生成する
4. `docs/` を commit / push する

CSV 列:

`id,name,category,cpu,memory,storage,os,use_case,pros,cons,rating,amazon_url,rakuten_url,last_checked`

- 文字コード: UTF-8（BOM 付きでも可）
- カンマを含む値は `"..."` で囲む（Excel 保存時も同様）
- 日本語を含む値もそのまま記述可能

商品名・スペック・リンクは `content/products.csv` を手動で更新してください。正確性は運営者が個別に確認する前提です。

## アフィリエイトリンク利用時の注意

- Amazonアソシエイト・楽天アフィリエイトの規約を遵守する
- 価格や在庫の自動取得は行わず、各販売ページで最新情報を確認するよう案内する
- ページ下部にアフィリエイト表記を記載する（`templates/index.html`）
- リンク先 URL は定期的に `check_links.py` と手動確認でメンテナンスする

## ライセンス

Private project（必要に応じて追記）
