# Accessibility and Mobility Lab Website

慶應義塾大学 理工学部 Accessibility and Mobility Lab の静的サイトを、JSON データと Python 3 スクリプトから `docs/` 以下へ生成するリポジトリです。GitHub Pages での公開を前提に、`docs/` をそのまま配信できる構成にしています。

## 構成

- `data/site.json`: 日英の研究室情報、研究内容、メンバー、関連リンク
- `data/publications.json`: Google Scholar から取得した業績データ
- `scripts/fetch_publications.py`: Google Scholar プロフィールを走査し、2019 年以降の業績を重複除去して保存
- `scripts/render_site.py`: `data/` の内容をもとに `docs/` を生成
- `scripts/serve_docs.py`: `docs/` をローカルで確認するための簡易 HTTP サーバー
- `docs/`: GitHub Pages 配信用の出力先

## 使い方

1. 業績データを更新します。

```bash
python3 scripts/fetch_publications.py
```

2. サイトを生成します。

```bash
python3 scripts/render_site.py
```

3. ローカルで確認します。

```bash
python3 scripts/serve_docs.py
```

`http://127.0.0.1:8002/` を開くと表示を確認できます。`serve_docs.py` は `docs/` を配信ルートにするので、ローカル確認では `/` が正規の URL です。互換性のため `/docs/` でもアクセスできます。

ポートを変更したい場合:

```bash
python3 scripts/serve_docs.py --port 8080
```

## GitHub Pages 公開

GitHub リポジトリの Settings > Pages で、公開元を以下のように設定します。

- Branch: `main`
- Folder: `/docs`

生成後の `docs/` をコミットすれば、そのまま `github.io` で公開できます。

## 補足

- 論文一覧は各メンバーの Google Scholar プロフィールから取得し、2019 年以降に絞って重複を除去します。
- Google Scholar 側の一時的な制限で取得に失敗する場合があります。その場合は時間をおいて `python3 scripts/fetch_publications.py` を再実行してください。
- 画像は仮のプレースホルダー SVG を出力しています。差し替える場合は `docs/assets/` 内の SVG を置き換えるか、`scripts/render_site.py` の画像参照先を変更してください。
