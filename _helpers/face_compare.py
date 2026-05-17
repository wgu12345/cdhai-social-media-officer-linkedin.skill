#!/usr/bin/env python3
"""
Identify a person's official photo via web search.

Usage:
    python3 face_compare.py --identify "Full Name"

Web-searches JHU / Carey / CDHAI / Hopkins pages for the named person.
Downloads the most-likely headshot. Caches it for 90 days. Returns JSON
with the cached path + source URL.

The face COMPARISON between this reference and candidate images is done
by Codex itself (multimodal native), not by this helper. This helper only
handles the deterministic parts: web search + image download.

Requires:
  - requests, beautifulsoup4 (installed by install.sh)
  - Optional: serpapi_key in ~/.cdhai-linkedin-skill/config.json for
    cleaner Google results; falls back to DuckDuckGo HTML otherwise.

NO OPENAI_API_KEY REQUIRED in v0.4.2 — Codex does the vision work itself.
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(json.dumps({"error": f"Missing dependency: {e}. Run install.sh."}))
    sys.exit(1)


CONFIG_PATH = Path.home() / ".cdhai-linkedin-skill" / "config.json"
CACHE_DIR = Path.home() / ".cdhai-linkedin-skill" / "cache"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 cdhai-skill/0.4.2"
)

QUERY_TEMPLATES = [
    '"{name}" Johns Hopkins Carey faculty',
    '"{name}" CDHAI Johns Hopkins',
    '"{name}" Hopkins medical AI',
    '"{name}" JHU faculty bio',
    '"{name}" Carey Business School',
]

PREFERRED_DOMAINS = ["carey.jhu.edu", "jhu.edu", "hopkinsmedicine.org", "cdhai.org"]


def name_hash(name: str) -> str:
    return hashlib.sha1(name.lower().strip().encode()).hexdigest()[:12]


def load_serpapi_key() -> str:
    if not CONFIG_PATH.exists():
        return ""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f).get("serpapi_key", "").strip()
    except Exception:
        return ""


def web_search_serpapi(query: str, key: str) -> list:
    try:
        r = requests.get("https://serpapi.com/search.json", params={
            "q": query, "engine": "google", "api_key": key, "num": 10
        }, timeout=15)
        r.raise_for_status()
        return [item.get("link", "") for item in r.json().get("organic_results", [])]
    except Exception:
        return []


def web_search_ddg(query: str) -> list:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.select("a.result__a"):
            href = a.get("href", "")
            if href.startswith("http") and "duckduckgo" not in href:
                links.append(href)
        return links[:10]
    except Exception:
        return []


def pick_best_link(links: list) -> str:
    for domain in PREFERRED_DOMAINS:
        for link in links:
            if domain in link:
                return link
    return links[0] if links else ""


def extract_headshot(page_url: str) -> tuple:
    try:
        r = requests.get(page_url, headers={"User-Agent": USER_AGENT}, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return urljoin(page_url, og["content"]), page_url

        candidates = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src:
                continue
            alt = img.get("alt", "").lower()
            classes = " ".join(img.get("class", [])).lower()
            score = 0
            if any(w in alt for w in ["portrait", "headshot", "photo", "profile"]):
                score += 3
            if any(w in classes for w in ["portrait", "headshot", "photo", "profile", "faculty", "bio"]):
                score += 3
            if any(w in src.lower() for w in ["headshot", "portrait", "faculty", "bio"]):
                score += 2
            if score > 0:
                candidates.append((score, urljoin(page_url, src)))

        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1], page_url

        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src and not src.endswith(".svg"):
                return urljoin(page_url, src), page_url
    except Exception:
        pass
    return None, page_url


def download_image(img_url: str, dest: Path):
    r = requests.get(img_url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)


def identify(name: str) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    nhash = name_hash(name)
    cache_img = CACHE_DIR / f"reference_{nhash}.jpg"

    if cache_img.exists():
        age_days = (time.time() - cache_img.stat().st_mtime) / 86400
        if age_days < 90:
            return {
                "name": name,
                "cached_image_path": str(cache_img),
                "source_url": "(cached)",
                "cache_age_days": round(age_days, 1),
            }

    serp_key = load_serpapi_key()
    found_links = []
    for tmpl in QUERY_TEMPLATES:
        q = tmpl.format(name=name)
        results = web_search_serpapi(q, serp_key) if serp_key else web_search_ddg(q)
        found_links.extend(results)
        if any(d in link for link in results for d in PREFERRED_DOMAINS):
            break

    if not found_links:
        return {
            "name": name, "cached_image_path": None, "source_url": None,
            "error": "No web search results found.",
        }

    best = pick_best_link(found_links)
    img_url, page_url = extract_headshot(best)

    if not img_url:
        return {
            "name": name, "cached_image_path": None, "source_url": page_url,
            "error": "Page found but no headshot extractable.",
        }

    try:
        download_image(img_url, cache_img)
    except Exception as e:
        return {
            "name": name, "cached_image_path": None, "source_url": page_url,
            "image_url": img_url, "error": f"Download failed: {e}",
        }

    return {
        "name": name,
        "cached_image_path": str(cache_img),
        "source_url": page_url,
        "image_url": img_url,
    }


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--identify":
        print("Usage: face_compare.py --identify \"Full Name\"", file=sys.stderr)
        print("", file=sys.stderr)
        print("(Face comparison itself is done by Codex natively; this helper only",
              file=sys.stderr)
        print(" handles web search + image download.)", file=sys.stderr)
        sys.exit(2)

    result = identify(sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
