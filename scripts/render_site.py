#!/usr/bin/env python3

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def e(value: str) -> str:
    return html.escape(value, quote=True)


def nav_items(lang: str) -> list[tuple[str, str]]:
    labels = {
        "ja": [
            ("mission", "ミッション"),
            ("research", "研究内容"),
            ("members", "メンバー"),
            ("publications", "業績"),
            ("access", "アクセス"),
            ("links", "関連リンク"),
        ],
        "en": [
            ("mission", "Mission"),
            ("research", "Research"),
            ("members", "Members"),
            ("publications", "Publications"),
            ("access", "Access"),
            ("links", "Related Links"),
        ],
    }
    return labels[lang]


def build_research_cards(site: dict, lang: str) -> str:
    chunks = []
    for area in site["research_areas"]:
        chunks.append(
            f"""
            <article class="card research-card">
              <h3>{e(area[f"{lang}_title"])}</h3>
              <p>{e(area[f"{lang}_body"])}</p>
            </article>
            """.strip()
        )
    return "\n".join(chunks)


def build_member_cards(site: dict, lang: str) -> str:
    chunks = []
    for member in site["members"]:
        chunks.append(
            f"""
            <article class="card member-card">
              <h3>{e(member[f"{lang}_name"])}</h3>
              <p><a href="{e(member['scholar_url'])}">Google Scholar</a></p>
            </article>
            """.strip()
        )
    return "\n".join(chunks)


def build_publication_items(publications: dict) -> str:
    if not publications["items"]:
        return '<li class="publication-item">Publication data has not been fetched yet.</li>'

    groups: dict[int, list[dict]] = {}
    for item in publications["items"]:
        groups.setdefault(item["year"], []).append(item)

    chunks = []
    for year in sorted(groups.keys(), reverse=True):
        items_html = []
        for item in groups[year]:
            meta = f"{item['authors']} / {item['venue']}"
            items_html.append(
                f"""
                <li class="publication-item">
                  <div>
                    <a href="{e(item['scholar_url'])}" class="publication-title">{e(item['title'])}</a>
                    <p>{e(meta)}</p>
                  </div>
                </li>
                """.strip()
            )
        chunks.append(
            f"""
            <section class="publication-year-group" aria-labelledby="pub-year-{year}">
              <h3 id="pub-year-{year}" class="publication-group-title">{year}</h3>
              <ol class="publication-list">
                {'\n'.join(items_html)}
              </ol>
            </section>
            """.strip()
        )
    return "\n".join(chunks)


def render_page(site: dict, publications: dict, lang: str) -> str:
    is_ja = lang == "ja"
    page_title = (
        f"{site['lab']['ja_name']} | {site['lab']['ja_affiliation']}"
        if is_ja
        else f"{site['lab']['en_name']} | {site['lab']['en_affiliation']}"
    )
    hero_name = site["lab"]["ja_name"] if is_ja else site["lab"]["en_name"]
    affiliation = site["lab"]["ja_affiliation"] if is_ja else site["lab"]["en_affiliation"]
    tagline = site["lab"]["ja_tagline"] if is_ja else site["lab"]["en_tagline"]
    overview = site["lab"]["ja_overview"] if is_ja else site["lab"]["en_overview"]
    mission_title = site["lab"]["ja_mission_title"] if is_ja else site["lab"]["en_mission_title"]
    mission_body = site["lab"]["ja_mission_body"] if is_ja else site["lab"]["en_mission_body"]
    contact_text = site["contact"]["ja_text"] if is_ja else site["contact"]["en_text"]
    publication_heading = "研究業績" if is_ja else "Publications"
    access_body = (
        "慶應義塾大学 理工学部キャンパス 34棟405号室を拠点としています。ページ内に埋め込んだ地図とマップリンクから場所をご確認いただけます。"
        if is_ja
        else "The lab is based in Room 405, Building 34, Faculty of Science and Technology, Keio University. You can check the embedded map below or open the full map in Google Maps."
    )
    links_heading = "関連リンク" if is_ja else "Related Links"
    members_heading = "メンバー" if is_ja else "Members"
    research_heading = "研究内容" if is_ja else "Research Areas"
    gallery_note = (
        "写真は後日追加予定です。現在はプレースホルダーを表示しています。"
        if is_ja
        else "Photos will be added later. Placeholder images are shown for now."
    )
    switch_label = "English" if is_ja else "日本語"
    switch_href = "../en/index.html" if is_ja else "../ja/index.html"
    updated_at = publications.get("generated_at")
    updated_label = ""
    if updated_at:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        updated_label = (
            f"最終更新: {dt.strftime('%Y-%m-%d %H:%M UTC')}"
            if is_ja
            else f"Last updated: {dt.strftime('%Y-%m-%d %H:%M UTC')}"
        )
    else:
        updated_label = "未取得" if is_ja else "Not fetched yet"

    nav_html = "".join(
        f'<li><a href="#{section_id}">{e(label)}</a></li>'
        for section_id, label in nav_items(lang)
    )
    related_html = "".join(
        f'<li><a href="{e(link["url"])}">{e(link[f"{lang}_label"])}</a></li>'
        for link in site["related_links"]
    )
    map_title = "慶應義塾大学 矢上キャンパスの地図" if is_ja else "Map of Keio University Yagami Campus"
    contact_link_label = site["contact"]["link_label_ja"] if is_ja else site["contact"]["link_label_en"]

    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(page_title)}</title>
  <meta name="description" content="{e(tagline)}">
  <link rel="stylesheet" href="../assets/site.css">
</head>
<body>
  <a class="skip-link" href="#main">{'本文へ移動' if is_ja else 'Skip to content'}</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="./index.html">
        <span class="brand-name">{e(hero_name)}</span>
        <span class="brand-affiliation">{e(affiliation)}</span>
      </a>
      <nav aria-label="Primary">
        <ul class="nav-list">
          {nav_html}
        </ul>
      </nav>
      <a class="lang-switch" href="{switch_href}" hreflang="{'en' if is_ja else 'ja'}" lang="{'en' if is_ja else 'ja'}">{e(switch_label)}</a>
    </div>
  </header>
  <main id="main">
    <section class="hero">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">{e(affiliation)}</p>
          <h1>{e(hero_name)}</h1>
          <p class="hero-tagline">{e(tagline)}</p>
          <p>{e(overview)}</p>
        </div>
        <div class="hero-visual">
          <img src="../assets/lab-placeholder.svg" alt="" width="640" height="480">
          <p class="image-note">{e(gallery_note)}</p>
        </div>
      </div>
    </section>

    <section id="mission" class="section">
      <div class="wrap section-grid">
        <div>
          <p class="section-kicker">{'ミッション' if is_ja else 'Mission'}</p>
          <h2>{e(mission_title)}</h2>
        </div>
        <p class="lead">{e(mission_body)}</p>
      </div>
    </section>

    <section id="research" class="section section-alt">
      <div class="wrap">
        <p class="section-kicker">{'研究' if is_ja else 'Research'}</p>
        <h2>{e(research_heading)}</h2>
        <div class="card-grid three-up">
          {build_research_cards(site, lang)}
        </div>
      </div>
    </section>

    <section id="members" class="section section-alt">
      <div class="wrap">
        <p class="section-kicker">{'メンバー' if is_ja else 'People'}</p>
        <h2>{e(members_heading)}</h2>
        <div class="card-grid two-up">
          {build_member_cards(site, lang)}
        </div>
      </div>
    </section>

    <section id="publications" class="section">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-kicker">Scholar</p>
            <h2>{e(publication_heading)}</h2>
          </div>
          <p class="section-meta">{e(updated_label)}</p>
        </div>
        {build_publication_items(publications)}
      </div>
    </section>

    <section id="access" class="section section-alt">
      <div class="wrap access-grid">
        <div>
          <p class="section-kicker">{'アクセス' if is_ja else 'Access'}</p>
          <h2>{'アクセス' if is_ja else 'Access'}</h2>
          <p>{e(access_body)}</p>
          <p><a class="button-link" href="{e(site['lab']['map_url'])}">{'Googleマップで見る' if is_ja else 'Open in Google Maps'}</a></p>
        </div>
        <div class="map-panel">
          <iframe
            class="map-embed"
            title="{e(map_title)}"
            src="{e(site['lab']['map_embed_url'])}"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
      </div>
    </section>

    <section id="links" class="section">
      <div class="wrap section-grid">
        <div>
          <p class="section-kicker">{'関連情報' if is_ja else 'Network'}</p>
          <h2>{e(links_heading)}</h2>
        </div>
        <div>
          <ul class="link-list">
            {related_html}
          </ul>
          <p class="contact-note">{e(contact_text)}<a href="{e(site['contact']['link_url'])}">{e(contact_link_label)}</a>{'まで。' if is_ja else '.'}</p>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <p>{e(hero_name)} / {e(affiliation)}</p>
      <p><a href="./index.html">{'ページ先頭へ戻る' if is_ja else 'Back to top'}</a></p>
    </div>
  </footer>
</body>
</html>
"""


def render_language_selector(site: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(site['lab']['en_name'])}</title>
  <link rel="stylesheet" href="./assets/site.css">
</head>
<body class="selector-body">
  <main class="selector-main">
    <p class="eyebrow">{e(site['lab']['en_affiliation'])}</p>
    <h1>{e(site['lab']['en_name'])}</h1>
    <p>{e(site['lab']['en_tagline'])}</p>
    <div class="selector-links">
      <a class="button-link" href="./ja/index.html">日本語</a>
      <a class="button-link button-secondary" href="./en/index.html">English</a>
    </div>
  </main>
</body>
</html>
"""


def write_assets() -> None:
    ensure_dir(ASSETS_DIR)
    css = """\
:root {
  --bg: #f6f2ea;
  --panel: #fffdf8;
  --panel-alt: #eae5d9;
  --text: #1c1a18;
  --muted: #5d5851;
  --line: #c9c0b2;
  --accent: #045b62;
  --accent-strong: #023b40;
  --focus: #d66a00;
  --shadow: 0 18px 40px rgba(28, 26, 24, 0.08);
  --radius: 20px;
  --wrap: min(1120px, calc(100vw - 2rem));
}

*,
*::before,
*::after { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  color: var(--text);
  background:
    radial-gradient(circle at top right, rgba(4, 91, 98, 0.14), transparent 26%),
    linear-gradient(180deg, #f9f7f2 0%, var(--bg) 100%);
  font-family: "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif;
  line-height: 1.7;
}

img { display: block; max-width: 100%; height: auto; }
a { color: var(--accent-strong); }
a:hover { color: var(--accent); }

.wrap { width: var(--wrap); margin: 0 auto; }

.skip-link {
  position: absolute;
  left: 1rem;
  top: -4rem;
  padding: 0.75rem 1rem;
  background: #fff;
  color: var(--text);
  z-index: 100;
}

.skip-link:focus { top: 1rem; outline: 3px solid var(--focus); }

.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(12px);
  background: rgba(249, 247, 242, 0.92);
  border-bottom: 1px solid rgba(201, 192, 178, 0.7);
}

.header-inner,
.footer-inner {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0;
}

.brand {
  display: inline-flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
}

.brand-name { font-weight: 800; font-size: 1.05rem; }
.brand-affiliation { color: var(--muted); font-size: 0.92rem; }

.nav-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-list a,
.lang-switch,
.button-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border-radius: 999px;
  padding: 0.7rem 1rem;
  text-decoration: none;
}

.nav-list a:hover,
.lang-switch:hover,
.button-link:hover { background: rgba(4, 91, 98, 0.08); }

.nav-list a:focus-visible,
.lang-switch:focus-visible,
.button-link:focus-visible,
a:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 3px;
}

.lang-switch,
.button-link {
  background: var(--accent);
  color: #fff;
  font-weight: 700;
}

.button-secondary {
  background: transparent;
  color: var(--accent-strong);
  border: 1px solid var(--line);
}

.hero,
.section { padding: 4.5rem 0; }

.hero-grid,
.section-grid,
.access-grid {
  display: grid;
  gap: 2rem;
  align-items: start;
}

.hero-grid { grid-template-columns: 1.2fr 1fr; min-height: 70svh; align-items: center; }
.section-grid,
.access-grid { grid-template-columns: 0.9fr 1.1fr; }

.eyebrow,
.section-kicker {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--accent);
}

h1, h2, h3 {
  line-height: 1.15;
  margin: 0 0 0.8rem;
}

h1 { font-size: clamp(2.4rem, 5vw, 4.8rem); max-width: 11ch; }
h2 { font-size: clamp(1.8rem, 3vw, 2.8rem); }
h3 { font-size: 1.2rem; }

p { margin: 0 0 1rem; }
.hero-tagline { font-size: clamp(1.1rem, 1.6vw, 1.35rem); color: var(--muted); }
.lead { font-size: clamp(1.1rem, 1.6vw, 1.35rem); }
.image-note, .section-meta, .contact-note, .member-role { color: var(--muted); }

.hero-visual img,
.selector-main,
.card,
.publication-list {
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.hero-visual img,
.map-embed {
  width: 100%;
  border-radius: var(--radius);
  background: var(--panel);
}

.section-alt { background: rgba(255, 253, 248, 0.7); }

.card-grid {
  display: grid;
  gap: 1.25rem;
}

.three-up { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.two-up { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.card {
  padding: 1.4rem;
  border-radius: var(--radius);
  background: var(--panel);
}

.member-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.section-head {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  align-items: end;
}

.publication-list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 1rem;
  border-radius: var(--radius);
  background: var(--panel);
}

.publication-year-group + .publication-year-group {
  margin-top: 1.5rem;
}

.publication-group-title {
  margin-bottom: 0.75rem;
  padding-left: 0.25rem;
}

.publication-item {
  display: grid;
  padding: 1rem 0;
  border-bottom: 1px solid var(--line);
}

.publication-item:last-child { border-bottom: 0; }
.publication-title { font-weight: 700; text-underline-offset: 0.2em; }

.link-list {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
}

.link-list li + li { margin-top: 0.75rem; }

.map-panel {
  border-radius: var(--radius);
  overflow: hidden;
}

.map-embed {
  min-height: 360px;
  border: 1px solid var(--line);
}

.site-footer {
  padding: 0.5rem 0 2rem;
  color: var(--muted);
}

.selector-body {
  min-height: 100svh;
  display: grid;
  place-items: center;
}

.selector-main {
  width: min(42rem, calc(100vw - 2rem));
  padding: 2rem;
  border-radius: calc(var(--radius) + 8px);
  background: var(--panel);
}

.selector-links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1.5rem;
}

@media (max-width: 960px) {
  .header-inner,
  .footer-inner,
  .section-head {
    flex-direction: column;
    align-items: start;
  }

  .hero-grid,
  .section-grid,
  .access-grid,
  .three-up,
  .two-up {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .hero,
  .section { padding: 3.25rem 0; }
}
"""
    lab_placeholder = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-labelledby="title desc">
  <title id="title">Placeholder image</title>
  <desc id="desc">Decorative placeholder for a future laboratory photo.</desc>
  <rect width="640" height="480" fill="#fffdf8"/>
  <rect x="24" y="24" width="592" height="432" rx="24" fill="#efe8d8" stroke="#8a7f70" stroke-width="3" stroke-dasharray="10 10"/>
  <path d="M120 332 L252 208 L352 292 L432 228 L520 332" fill="none" stroke="#045b62" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="220" cy="150" r="36" fill="#d1e3e4"/>
  <text x="320" y="390" text-anchor="middle" font-size="28" font-family="sans-serif" fill="#5d5851">Photo placeholder</text>
</svg>
"""
    member_placeholder = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" role="img" aria-labelledby="title desc">
  <title id="title">Portrait placeholder</title>
  <desc id="desc">Decorative placeholder for a future member portrait.</desc>
  <rect width="320" height="240" fill="#fffdf8"/>
  <rect x="18" y="18" width="284" height="204" rx="18" fill="#e8eee9" stroke="#8a7f70" stroke-width="2.5" stroke-dasharray="8 8"/>
  <circle cx="160" cy="100" r="38" fill="#d8d0c2"/>
  <path d="M95 185 C110 150, 210 150, 225 185" fill="#d8d0c2"/>
  <text x="160" y="214" text-anchor="middle" font-size="18" font-family="sans-serif" fill="#5d5851">Member photo</text>
</svg>
"""
    (ASSETS_DIR / "site.css").write_text(css, encoding="utf-8")
    (ASSETS_DIR / "lab-placeholder.svg").write_text(lab_placeholder, encoding="utf-8")
    (ASSETS_DIR / "member-placeholder.svg").write_text(member_placeholder, encoding="utf-8")


def main() -> int:
    site = load_json(DATA_DIR / "site.json")
    publications = load_json(DATA_DIR / "publications.json")
    ensure_dir(DOCS_DIR / "ja")
    ensure_dir(DOCS_DIR / "en")
    write_assets()
    (DOCS_DIR / "index.html").write_text(render_language_selector(site), encoding="utf-8")
    (DOCS_DIR / "ja" / "index.html").write_text(render_page(site, publications, "ja"), encoding="utf-8")
    (DOCS_DIR / "en" / "index.html").write_text(render_page(site, publications, "en"), encoding="utf-8")
    print("Rendered site into docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
