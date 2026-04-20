# Accessibility and Mobility Lab Website

慶應義塾大学 理工学研究科 Accessibility and Mobility Lab の静的サイト生成用リポジトリです。出力先は `docs/` です。

## 更新

```bash
python3 scripts/fetch_publications.py
python3 scripts/render_site.py
python3 scripts/serve_docs.py
```

ローカル確認: `http://127.0.0.1:8002/`

## 公開

GitHub Pages: `main` ブランチの `/docs`
