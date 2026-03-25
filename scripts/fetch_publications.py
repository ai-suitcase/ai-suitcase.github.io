#!/usr/bin/env python3

from __future__ import annotations

import html
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SITE_DATA_PATH = ROOT / "data" / "site.json"
PUBLICATIONS_PATH = ROOT / "data" / "publications.json"
YEAR_FROM = 2019
USER_AGENT = "Mozilla/5.0 (compatible; AccessibilityMobilityLabBot/1.0)"
ROW_RE = re.compile(
    r'<tr class="gsc_a_tr">.*?'
    r'<a href="([^"]+)" class="gsc_a_at">(.*?)</a>'
    r'<div class="gs_gray">(.*?)</div>'
    r'<div class="gs_gray">(.*?)</div>.*?'
    r'<td class="gsc_a_y"><span class="gsc_a_h gsc_a_hc gs_ibl">(\d{4})</span>',
    re.S,
)


def load_site_data() -> dict:
    return json.loads(SITE_DATA_PATH.read_text(encoding="utf-8"))


def clean_html_text(value: str) -> str:
    text = re.sub(r"<.*?>", "", value)
    text = html.unescape(text)
    return " ".join(text.split())


def normalize_title(title: str) -> str:
    text = unicodedata.normalize("NFKC", title).casefold()
    return re.sub(r"[\W_]+", "", text)


def should_skip_entry(venue: str) -> bool:
    lower = venue.casefold()
    if "patent" in lower or "thesis" in lower:
        return True
    if re.fullmatch(r".*university,\s*\d{4}", lower):
        return True
    return False


def fetch_scholar_page(user_id: str, start: int) -> str:
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en&cstart={start}&pagesize=100"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def extract_member_publications(user_id: str) -> list[dict]:
    publications: list[dict] = []
    start = 0
    while True:
        html_text = fetch_scholar_page(user_id, start)
        rows = ROW_RE.findall(html_text)
        if not rows:
            break

        for href, title, authors, venue, year_text in rows:
            year = int(year_text)
            if year < YEAR_FROM:
                continue

            title_text = clean_html_text(title)
            authors_text = clean_html_text(authors)
            venue_text = clean_html_text(venue)
            if should_skip_entry(venue_text):
                continue

            publications.append(
                {
                    "title": title_text,
                    "authors": authors_text,
                    "venue": venue_text,
                    "year": year,
                    "scholar_url": f"https://scholar.google.com{html.unescape(href)}",
                }
            )

        if len(rows) < 100:
            break
        start += 100
        time.sleep(0.5)

    return publications


def deduplicate_publications(items: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for item in items:
        key = normalize_title(item["title"])
        current = deduped.get(key)
        if current is None:
            deduped[key] = item
            continue

        better = item
        if len(current["authors"]) > len(item["authors"]):
            better = current
        elif current["year"] > item["year"]:
            better = current
        deduped[key] = better

    return sorted(
        deduped.values(),
        key=lambda item: (-item["year"], normalize_title(item["title"])),
    )


def main() -> int:
    site_data = load_site_data()
    user_ids = []
    for member in site_data["members"]:
        match = re.search(r"user=([^&]+)", member["scholar_url"])
        if not match:
            continue
        user_ids.append(match.group(1))

    try:
        items: list[dict] = []
        for user_id in user_ids:
            items.extend(extract_member_publications(user_id))
            time.sleep(0.5)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Failed to fetch Google Scholar data: {exc}", file=sys.stderr)
        return 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Google Scholar",
        "year_from": YEAR_FROM,
        "items": deduplicate_publications(items),
    }
    PUBLICATIONS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(payload['items'])} publications to {PUBLICATIONS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
