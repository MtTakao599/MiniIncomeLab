# MiniIncomeLab

ミニPC上の Ubuntu で定期実行し、静的サイトを自動生成するアフィリエイト/情報サイト生成ツール（v0.1）。

- **開発**: Windows + Cursor
- **管理**: GitHub
- **生成**: Python + CSV + HTML テンプレート（標準ライブラリのみ）
- **公開**: GitHub Pages または Cloudflare Pages（`docs/` をそのまま公開）
- **実行環境**: ミニPC（Ubuntu、外部公開なし）

## プロジェクト概要

MiniIncomeLab は、商品情報を `content/products.csv` に手動で書き込み、`scripts/build_site.py` で静的 HTML を生成する最小構成のサイトビルダーです。

v0.1 では「ミニPC比較サイト」の一覧ページ（`docs/index.html`）のみを対象としています。将来的には中古PC、Linux、タイ移住準備、管理人便利グッズなどへ横展開できるよう、CSV + テンプレート構成を維持します。

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
    articles/             # 将来の記事用
  templates/
    base.html             # 共通レイアウト + CSS
    index.html            # トップページ
    product_card.html     # 商品カード
  scripts/
    build_site.py         # サイト生成
    check_links.py        # リンク簡易チェック
  docs/                   # 生成された静的ファイル（公開ディレクトリ）
    index.html
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
- [ ] `docs\index.html` と `docs\.nojekyll` が Git のコミット対象になる

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
| `--clean` | 再生成前に `docs/index.html` など既知の生成物を削除 |
| `--open` | 生成後に既定ブラウザで `docs/index.html` を開く |

ビルド結果は `logs\build.log` に記録されます（追記方式）。

## Ubuntu での実行方法

```bash
cd /home/koishi/MiniIncomeLab
python3 scripts/check_links.py
python3 scripts/build_site.py --clean
```

生成物は `docs/index.html` です。パスは `pathlib.Path` を使っているため、Windows / Linux どちらでも同じスクリプトが動きます。

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

現在のサンプル商品（3件）はすべて【サンプル】表記の仮データです。実在商品の正確なスペック・価格は後から手動で差し替えてください。

## アフィリエイトリンク利用時の注意

- Amazonアソシエイト・楽天アフィリエイトの規約を遵守する
- 価格や在庫の自動取得は行わず、各販売ページで最新情報を確認するよう案内する
- ページ下部にアフィリエイト表記を記載する（`templates/index.html`）
- リンク先 URL は定期的に `check_links.py` と手動確認でメンテナンスする

## ライセンス

Private project（必要に応じて追記）
