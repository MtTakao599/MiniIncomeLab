# MiniIncomeLab

ミニPC上の Ubuntu で定期実行し、静的サイトを自動生成するアフィリエイト/情報サイト生成ツール（v0.1.7）。

- **開発**: Windows + Cursor
- **管理**: GitHub
- **生成**: Python + CSV + HTML テンプレート（標準ライブラリのみ）
- **公開**: GitHub Pages または Cloudflare Pages（`docs/` をそのまま公開）
- **実行環境**: ミニPC（Ubuntu、外部公開なし）

## プロジェクト概要

MiniIncomeLab は、商品情報を `content/products_source.csv`、アフィリエイトリンクを `content/affiliate_links.csv` に分けて管理し、`scripts/build_site.py` で静的 HTML を生成する最小構成のサイトビルダーです。

v0.1.7 では、**商品情報とアフィリエイトリンクの分離**に対応しました。リンクだけを手動管理し、商品説明・スペック側の上書き事故を防ぎます。

**v0.1.7 時点の参加状況:**

- **楽天アフィリエイト**: 利用中（リンクは `affiliate_links.csv` の `rakuten_url` に手動で貼る）
- **Amazonアソシエイト**: 未参加（`amazon_url` は空欄のまま）
- 価格・在庫・仕様の自動取得、スクレイピング、API 連携は行わない

> **移行メモ:** 旧 `content/products.csv` は v0.1.7 で廃止しました。利用しないでください。

### 2ファイル構成（v0.1.7）

| ファイル | 役割 | 誰が触るか |
|---------|------|-----------|
| `products_source.csv` | 商品名・スペック・用途・status など | 自動更新 / 半自動更新の対象 |
| `affiliate_links.csv` | Amazon / 楽天リンクのみ | **普段は小石さんが手動更新** |

リンクファイルを分けることで、商品情報の更新時にアフィリエイト URL を誤って上書きする事故を防ぎます。

### 日常運用ルール
- **`affiliate_links.csv` 以外は毎日編集しない**（記事や固定ページのビルドだけ毎日回す）
- **週1回〜月1回**、`affiliate_links.csv` のリンクと `products_source.csv` の内容を確認する
- **ミニPC（Ubuntu）** では毎日 `git pull` → `check_links.py` → `build_site.py --clean` を自動実行する
- 商品を一時的に非表示にしたい場合は **`status=hidden`**
- 下書きとして保管したい場合は **`status=draft`**
- 公開する商品だけ **`status=active`**

### Amazon 申請前の方針

Amazonアソシエイト申請前に、**10 記事程度のオリジナルコンテンツ**を `content/articles/` に用意する方針です。v0.1.3 で記事 10 本、v0.1.4 で運営者情報・プライバシーポリシーを整備済みです。v0.1.5 では問い合わせ導線の文言調整と、全ページ共通の内部リンク整備を行っています。

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
    products_source.csv   # 商品情報（スペック・説明・status）
    affiliate_links.csv   # アフィリエイトリンク（手動管理）
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
- [ ] ブラウザで **active** の商品カードのみ表示される（`draft` / `hidden` は非表示）
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

### サイト更新日

トップページと記事ページに表示する **サイト更新日 / 最終更新日** は、`build_site.py` 実行日（`YYYY-MM-DD`）です。ビルドのたびに更新されます。

### 記事一覧の並び順

記事一覧は **`content/articles/*.md` のファイル名（slug）昇順** で固定しています。現在の並び:

1. always-on-mini-pc
2. linux-mini-pc
3. mini-pc-storage-memory
4. mini-pc-trouble-check
5. mini-pc-vs-laptop
6. n100-mini-pc
7. n150-mini-pc
8. ryzen-mini-pc
9. used-mini-pc
10. windows-mini-pc

並び順を変えたい場合は、ファイル名を変更するか、`scripts/build_site.py` の `load_articles()` を拡張してください。

## cron で毎日 4 時に実行する例

ミニPC（Ubuntu）で crontab を編集します。

```bash
crontab -e
```

以下を追加します。`git pull` で最新の CSV / 記事を取得してから、リンクチェックとビルドを行います。

```cron
0 4 * * * cd /home/koishi/MiniIncomeLab && git pull >> logs/cron.log 2>&1 && /usr/bin/python3 scripts/check_links.py >> logs/cron.log 2>&1 && /usr/bin/python3 scripts/build_site.py --clean >> logs/cron.log 2>&1
```

- 毎日自動実行するのは **pull / check / build** のみ
- **`affiliate_links.csv` の編集**は週1回〜月1回の手動確認時で十分
- ビルド後に GitHub Pages へ反映する場合は、必要に応じて `docs/` を commit / push する（v0.2 以降で自動化を検討）

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

## 商品情報とリンクの更新

### 商品情報（products_source.csv）

1. `content/products_source.csv` を編集する
2. `python scripts/build_site.py --clean` で再生成する

列:

`id,status,name,category,cpu,memory,storage,os,use_case,pros,cons,rating,last_checked`

`status` の値:

| 値 | 意味 |
|----|------|
| `active` | サイトに表示する |
| `draft` | 下書き（非表示） |
| `hidden` | 非表示（一時的に掲載停止） |

### アフィリエイトリンク（affiliate_links.csv）

1. 楽天アフィリエイト（または将来の Amazon）管理画面でリンクを取得する
2. `content/affiliate_links.csv` の該当 `id` 行に URL を貼り付ける
3. `python scripts/check_links.py` で URL 形式を確認する（空欄は許容、不正 URL のみエラー）
4. `python scripts/build_site.py --clean` で再生成する

列:

`id,amazon_url,rakuten_url,note`

- `id` は `products_source.csv` と同じ値に揃える
- `note` は用途メモ用（サイトには表示されない）
- リンク行がなくてもビルドは続行（購入ボタンは「準備中」表示）

### 共通ルール

- 文字コード: UTF-8（BOM 付きでも可）
- カンマを含む値は `"..."` で囲む（Excel 保存時も同様）
- 日本語を含む値もそのまま記述可能
- 更新後は `docs/` を commit / push する

## アフィリエイトリンク利用時の注意

- **楽天アフィリエイト**: 利用中。規約を遵守し、`affiliate_links.csv` の `rakuten_url` を手動更新する
- **Amazonアソシエイト**: 未参加。参加後に `affiliate_links.csv` の `amazon_url` を更新する
- 価格や在庫の自動取得は行わず、各販売ページで最新情報を確認するよう案内する
- ページ下部にアフィリエイト表記を記載する（`templates/index.html` 等）
- リンク先 URL は定期的に `check_links.py` と手動確認でメンテナンスする

## ライセンス

Private project（必要に応じて追記）
