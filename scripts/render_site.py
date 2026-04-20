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


def localized_field(data: dict, lang: str, key: str) -> str:
    return data[f"{lang}_{key}"]


def nav_items(site: dict, lang: str) -> list[tuple[str, str]]:
    return [(item["id"], item["label"]) for item in site["ui"][lang]["nav"]]


def build_research_cards(site: dict, lang: str, ui: dict) -> str:
    chunks = []
    card_label = ui["research_card_label"]
    for index, area in enumerate(site["research_areas"], start=1):
        chunks.append(
            f"""
            <article class="card research-card">
              <p class="card-index">{index:02d} / {e(card_label)}</p>
              <h3>{e(area[f"{lang}_title"])}</h3>
              <p>{e(area[f"{lang}_body"])}</p>
            </article>
            """.strip()
        )
    return "\n".join(chunks)


def build_member_cards(site: dict, lang: str, asset_prefix: str, ui: dict) -> str:
    chunks = []
    for member in site["members"]:
        member_name = localized_field(member, lang, "name")
        photo_alt = ui["member_photo_alt"].format(name=member_name)
        chunks.append(
            f"""
            <article class="card member-card">
              <div class="member-photo-frame">
                <img class="member-photo" src="{e(asset_prefix)}/member-placeholder.svg" alt="{e(photo_alt)}" width="320" height="240">
              </div>
              <div class="member-details">
                <h3>{e(member_name)}</h3>
                <p><a class="text-link" href="{e(member['scholar_url'])}">{e(ui["scholar_link_label"])}</a></p>
              </div>
            </article>
            """.strip()
        )
    return "\n".join(chunks)


def build_publication_items(publications: dict, ui: dict) -> str:
    if not publications["items"]:
        return f'<li class="publication-item">{e(ui["publication_empty"])}</li>'

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


def render_page(
    site: dict,
    publications: dict,
    lang: str,
    *,
    asset_prefix: str = "../assets",
    switch_href: str | None = None,
    home_href: str = "./index.html",
) -> str:
    is_ja = lang == "ja"
    ui = site["ui"][lang]
    page_title = (
        f"{localized_field(site['lab'], lang, 'name')} | {localized_field(site['lab'], lang, 'affiliation')}"
        if is_ja
        else f"{localized_field(site['lab'], lang, 'name')} | {localized_field(site['lab'], lang, 'affiliation')}"
    )
    hero_name = localized_field(site["lab"], lang, "name")
    affiliation = localized_field(site["lab"], lang, "affiliation")
    tagline = localized_field(site["lab"], lang, "tagline")
    overview = localized_field(site["lab"], lang, "overview")
    mission_title = localized_field(site["lab"], lang, "mission_title")
    mission_body = localized_field(site["lab"], lang, "mission_body")
    contact_text = localized_field(site["contact"], lang, "text")
    contact_link_label = site["contact"][f"link_label_{lang}"]
    publication_heading = ui["publication_heading"]
    access_body = ui["access_body"]
    links_heading = ui["links_heading"]
    members_heading = ui["members_heading"]
    research_heading = ui["research_heading"]
    switch_label = ui["switch_label"]
    if switch_href is None:
        switch_href = "../en/index.html" if is_ja else "../ja/index.html"
    updated_at = publications.get("generated_at")
    if updated_at:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        updated_label = f"{ui['updated_prefix']}{dt.strftime('%Y-%m-%d %H:%M UTC')}"
    else:
        updated_label = ui["not_fetched"]

    nav_html = "".join(
        f'<li><a href="#{section_id}">{e(label)}</a></li>'
        for section_id, label in nav_items(site, lang)
    )
    related_html = "".join(
        f'<li><a href="{e(link["url"])}">{e(link[f"{lang}_label"])}</a></li>'
        for link in site["related_links"]
    )
    map_title = ui["map_title"]
    hero_primary_href = "#research"
    hero_primary_label = ui["hero_primary_label"]
    hero_secondary_href = "#publications"
    hero_secondary_label = ui["hero_secondary_label"]
    visual_kicker = localized_field(site["lab"], lang, "prototype_kicker")
    visual_title = localized_field(site["lab"], lang, "prototype_title")
    visual_body = localized_field(site["lab"], lang, "prototype_body")
    hero_background_style = (
        "background-image: "
        "linear-gradient(90deg, rgba(255, 249, 240, 1.00) 0%, rgba(255, 249, 240, 0.96) 40%, rgba(255, 249, 240, 0.75) 100%), "
        f"url('{e(asset_prefix)}/hero-photo.jpg');"
    )

    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(page_title)}</title>
  <meta name="description" content="{e(tagline)}">
  <link rel="stylesheet" href="{e(asset_prefix)}/site.css">
</head>
<body>
  <a class="skip-link" href="#main">{e(ui["skip_link"])}</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="{e(home_href)}">
        <span class="brand-name">{e(hero_name)}</span>
        <span class="brand-affiliation">{e(affiliation)}</span>
      </a>
      <nav aria-label="{e(ui['primary_nav_label'])}">
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
        <div class="hero-copy panel" style="{hero_background_style}">
          <p class="eyebrow">{e(affiliation)}</p>
          <h1>{e(hero_name)}</h1>
          <p class="hero-tagline">{e(tagline)}</p>
          <p>{e(overview)}</p>
          <div class="hero-actions">
            <a class="button-link" href="{hero_primary_href}">{e(hero_primary_label)}</a>
            <a class="button-link button-secondary" href="{hero_secondary_href}">{e(hero_secondary_label)}</a>
          </div>
        </div>
      </div>
    </section>

    <section id="mission" class="section">
      <div class="wrap section-grid">
        <div>
          <p class="section-kicker">{e(ui["mission_kicker"])}</p>
          <h2>{e(mission_title)}</h2>
        </div>
        <p class="lead">{e(mission_body)}</p>
      </div>
    </section>

    <!-- 一旦コメントアウト
    <section class="section">
      <div class="wrap section-grid">
        <div>
          <p class="section-kicker hero-kicker">{e(visual_kicker)}</p>
          <h2>{e(visual_title)}</h2>
        </div>
        <div class="prototype-content">
          <p class="lead">{e(visual_body)}</p>
        </div>
      </div>
    </section>
    -->

    <section id="research" class="section section-alt">
      <div class="wrap">
        <p class="section-kicker">{e(ui["research_kicker"])}</p>
        <h2>{e(research_heading)}</h2>
        <div class="card-grid three-up">
          {build_research_cards(site, lang, ui)}
        </div>
      </div>
    </section>

    <section id="members" class="section section-alt">
      <div class="wrap">
        <p class="section-kicker">{e(ui["members_kicker"])}</p>
        <h2>{e(members_heading)}</h2>
        <div class="card-grid two-up">
          {build_member_cards(site, lang, asset_prefix, ui)}
        </div>
      </div>
    </section>

    <section id="publications" class="section">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-kicker">{e(ui["publication_kicker"])}</p>
            <h2>{e(publication_heading)}</h2>
          </div>
          <p class="section-meta">{e(updated_label)}</p>
        </div>
        {build_publication_items(publications, ui)}
      </div>
    </section>

    <section id="access" class="section section-alt">
      <div class="wrap access-grid">
        <div>
          <p class="section-kicker">{e(ui["access_kicker"])}</p>
          <h2>{e(ui["access_heading"])}</h2>
          <p>{e(access_body)}</p>
          <p><a class="button-link" href="{e(site['lab']['map_url'])}">{e(ui["map_button_label"])}</a></p>
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
          <p class="section-kicker">{e(ui["links_kicker"])}</p>
          <h2>{e(links_heading)}</h2>
        </div>
        <div>
          <ul class="link-list">
            {related_html}
          </ul>
          <p class="contact-note">{e(contact_text)}<a href="{e(site['contact']['link_url'])}">{e(contact_link_label)}</a>{e(ui["contact_suffix"])}</p>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <p>{e(hero_name)} / {e(affiliation)}</p>
      <p><a href="{e(home_href)}">{e(ui["back_to_top"])}</a></p>
    </div>
  </footer>
</body>
</html>
"""


def write_assets(site: dict) -> None:
    ensure_dir(ASSETS_DIR)
    asset_ui = site["ui"]["assets"]
    css = """\
:root {
  --bg: #f5efe3;
  --bg-strong: #efe2cb;
  --panel: rgba(255, 250, 241, 0.8);
  --panel-solid: #fff8ee;
  --panel-strong: rgba(255, 244, 224, 0.95);
  --text: #172126;
  --muted: #5f6368;
  --line: rgba(23, 33, 38, 0.12);
  --accent: #ef5b2a;
  --accent-strong: #b53a12;
  --accent-alt: #0f766e;
  --accent-soft: #ffd166;
  --focus: #1d4ed8;
  --shadow: 0 28px 60px rgba(23, 33, 38, 0.12);
  --radius: 28px;
  --wrap: min(1160px, calc(100vw - 2rem));
}

*,
*::before,
*::after { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  position: relative;
  margin: 0;
  min-height: 100vh;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 12%, rgba(239, 91, 42, 0.26), transparent 22%),
    radial-gradient(circle at 86% 16%, rgba(15, 118, 110, 0.18), transparent 24%),
    radial-gradient(circle at 78% 78%, rgba(255, 209, 102, 0.28), transparent 24%),
    linear-gradient(180deg, #fbf6ed 0%, var(--bg) 46%, var(--bg-strong) 100%);
  font-family: "Avenir Next", "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif;
  line-height: 1.7;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(23, 33, 38, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 33, 38, 0.035) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.58), transparent 82%);
  pointer-events: none;
  z-index: -1;
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
  backdrop-filter: blur(18px);
  background: rgba(251, 246, 237, 0.78);
  border-bottom: 1px solid rgba(23, 33, 38, 0.08);
}

.header-inner,
.footer-inner {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0;
}

.header-inner { gap: 0.8rem; }

.brand {
  display: inline-flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
}

.brand-name {
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: 0.02em;
}

.brand-affiliation { color: var(--muted); font-size: 0.92rem; }

.nav-list {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.5rem;
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
  padding: 0.72rem 1.05rem;
  text-decoration: none;
  transition: transform 180ms ease, background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.nav-list a {
  color: var(--text);
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(23, 33, 38, 0.08);
  padding: 0.62rem 0.85rem;
  font-size: 0.94rem;
  white-space: nowrap;
}

.nav-list a:hover,
.lang-switch:hover,
.button-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(23, 33, 38, 0.08);
}

.nav-list a:hover { background: rgba(255, 255, 255, 0.78); }

.nav-list a:focus-visible,
.lang-switch:focus-visible,
.button-link:focus-visible,
a:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 3px;
}

.lang-switch,
.button-link {
  background: linear-gradient(135deg, var(--accent) 0%, #ff855c 100%);
  color: #fff;
  font-weight: 700;
  border: 1px solid rgba(181, 58, 18, 0.25);
}

.button-secondary {
  background: rgba(255, 255, 255, 0.6);
  color: var(--text);
  border: 1px solid rgba(23, 33, 38, 0.12);
}

.panel,
.card,
.publication-list,
.selector-main,
.map-panel {
  position: relative;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
}

.panel::before,
.card::before,
.publication-list::before,
.selector-main::before,
.map-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(255, 255, 255, 0.55);
  pointer-events: none;
}

.hero,
.section { padding: 4.75rem 0; }

.hero {
  position: relative;
  overflow: clip;
}

.hero::after {
  content: "";
  position: absolute;
  right: -8rem;
  top: 3rem;
  width: min(38vw, 460px);
  aspect-ratio: 1;
  border-radius: 32% 68% 66% 34% / 34% 39% 61% 66%;
  background:
    linear-gradient(135deg, rgba(15, 118, 110, 0.24), rgba(255, 209, 102, 0.18)),
    rgba(255, 255, 255, 0.28);
  filter: blur(10px);
  z-index: -1;
}

.hero-grid,
.section-grid,
.access-grid {
  display: grid;
  gap: 2rem;
  align-items: start;
}

.hero-grid {
  grid-template-columns: 1fr;
  align-items: stretch;
}

.section-grid,
.access-grid { grid-template-columns: 0.9fr 1.1fr; }

.hero-copy {
  border-radius: calc(var(--radius) + 8px);
  padding: 1.75rem;
  background-position: 0 0, 300px center;
  background-size: auto, cover;
  background-repeat: repeat, no-repeat;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: min(78svh, 760px);
}

.prototype-content {
  display: grid;
  gap: 1.25rem;
}

.card-index {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  width: fit-content;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  background: rgba(15, 118, 110, 0.08);
  color: var(--accent-alt);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.eyebrow,
.section-kicker {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.76rem;
  font-weight: 800;
  color: var(--accent-alt);
}

h1, h2, h3 {
  line-height: 1.08;
  margin: 0 0 0.8rem;
}

h1 {
  font-size: clamp(3rem, 6vw, 5.8rem);
  max-width: 11ch;
  letter-spacing: -0.04em;
}

h2 {
  font-size: clamp(2rem, 3vw, 3.2rem);
  letter-spacing: -0.03em;
}

h3 { font-size: 1.3rem; }

p { margin: 0 0 1rem; }

.hero-tagline,
.lead {
  font-size: clamp(1.1rem, 1.8vw, 1.45rem);
}

.hero-tagline {
  max-width: 40rem;
  color: #26343b;
  margin-bottom: 1.2rem;
}

.hero-copy > p:not(.eyebrow):not(.section-kicker):not(.hero-tagline) {
  font-size: clamp(1.05rem, 1.45vw, 1.18rem);
}

.hero-kicker {
  margin-bottom: 0.9rem;
}

.image-note,
.section-meta,
.contact-note {
  color: var(--muted);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin: 1rem 0 1.5rem;
}

.visual-callout {
  width: 100%;
  padding: 1.1rem 1.2rem 0.2rem;
  border-radius: 24px;
  background: rgba(255, 249, 238, 0.82);
  border: 1px solid rgba(23, 33, 38, 0.08);
}

.section-alt {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 248, 238, 0.48));
  border-top: 1px solid rgba(23, 33, 38, 0.05);
  border-bottom: 1px solid rgba(23, 33, 38, 0.05);
}

.card-grid {
  display: grid;
  gap: 1.25rem;
}

.three-up { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.two-up { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.card {
  padding: 1.5rem;
  border-radius: var(--radius);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 248, 238, 0.9)),
    var(--panel);
}

.research-card h3,
.member-card h3 { margin-top: 0.35rem; }

.member-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.5rem;
  align-items: center;
  min-height: 100%;
}

.member-photo-frame {
  overflow: hidden;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(255, 209, 102, 0.18)),
    rgba(255, 249, 238, 0.92);
  border: 1px solid rgba(23, 33, 38, 0.08);
}

.member-photo {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.member-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.member-details h3 {
  margin-top: 0;
  margin-bottom: 0.8rem;
}

.text-link {
  font-weight: 700;
  text-underline-offset: 0.2em;
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
  padding: 1rem 1.2rem;
  border-radius: var(--radius);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(255, 247, 235, 0.88));
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
  border-bottom: 1px solid rgba(23, 33, 38, 0.08);
}

.publication-item:last-child { border-bottom: 0; }

.publication-title {
  font-weight: 700;
  text-underline-offset: 0.2em;
}

.link-list {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
}

.link-list li + li { margin-top: 0.8rem; }

.map-panel {
  border-radius: calc(var(--radius) + 4px);
  overflow: hidden;
  background: rgba(255, 249, 238, 0.72);
}

.map-embed {
  width: 100%;
  min-height: 360px;
  border: 0;
  background: var(--panel-solid);
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
  padding: 2.25rem;
  border-radius: calc(var(--radius) + 10px);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.9), rgba(255, 244, 224, 0.88));
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

  .member-card {
    grid-template-columns: 1fr;
    align-items: start;
  }

  h1 { max-width: none; }
}

@media (max-width: 720px) {
  .hero,
  .section { padding: 3.5rem 0; }

  .hero-copy,
  .selector-main,
  .card,
  .publication-list {
    padding: 1.25rem;
  }

  .nav-list { gap: 0.5rem; }
}
"""
    lab_placeholder = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-labelledby="title desc">
  <title id="title">{e(asset_ui['lab_placeholder']['title'])}</title>
  <desc id="desc">{e(asset_ui['lab_placeholder']['desc'])}</desc>
  <rect width="640" height="480" fill="#fffdf8"/>
  <rect x="24" y="24" width="592" height="432" rx="24" fill="#efe8d8" stroke="#8a7f70" stroke-width="3" stroke-dasharray="10 10"/>
  <path d="M120 332 L252 208 L352 292 L432 228 L520 332" fill="none" stroke="#045b62" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="220" cy="150" r="36" fill="#d1e3e4"/>
  <text x="320" y="390" text-anchor="middle" font-size="28" font-family="sans-serif" fill="#5d5851">{e(asset_ui['lab_placeholder']['caption'])}</text>
</svg>
"""
    member_placeholder = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" role="img" aria-labelledby="title desc">
  <title id="title">{e(asset_ui['member_placeholder']['title'])}</title>
  <desc id="desc">{e(asset_ui['member_placeholder']['desc'])}</desc>
  <rect width="320" height="240" fill="#fffdf8"/>
  <rect x="18" y="18" width="284" height="204" rx="18" fill="#e8eee9" stroke="#8a7f70" stroke-width="2.5" stroke-dasharray="8 8"/>
  <circle cx="160" cy="100" r="38" fill="#d8d0c2"/>
  <path d="M95 185 C110 150, 210 150, 225 185" fill="#d8d0c2"/>
  <text x="160" y="214" text-anchor="middle" font-size="18" font-family="sans-serif" fill="#5d5851">{e(asset_ui['member_placeholder']['caption'])}</text>
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
    write_assets(site)
    (DOCS_DIR / "index.html").write_text(
        render_page(
            site,
            publications,
            "ja",
            asset_prefix="./assets",
            switch_href="./en/index.html",
            home_href="./index.html",
        ),
        encoding="utf-8",
    )
    (DOCS_DIR / "ja" / "index.html").write_text(render_page(site, publications, "ja"), encoding="utf-8")
    (DOCS_DIR / "en" / "index.html").write_text(render_page(site, publications, "en"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
