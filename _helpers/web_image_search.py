#!/usr/bin/env python3
"""
Web image search (Tier 3 option c).

⚠️  LEGAL WARNING ⚠️

Every image returned by this helper REQUIRES manual usage-rights
verification before posting on JHU / CDHAI / Carey accounts. Random
web images are typically copyrighted. Using them without a license is
legal exposure for the institution.

Acceptable uses of a web-sourced image are limited to:
  1. Public domain works (verified at the source).
  2. Images the user has obtained explicit written permission to use.
  3. Images under a license that permits the intended use (CC-BY,
     CC0, etc.), with proper attribution if required.

The skill flags every web-sourced image prominently in the report.
The user is responsible for the final usage-rights decision.

---

Usage:
    python3 web_image_search.py "<query>" [--max 5]
    python3 web_image_search.py "<query>" --download <index>

Returns JSON with candidate images (URLs, source pages, titles). Use
--download <index> to fetch and cache one result.

No API key required (uses Bing HTML scraping). Falls back gracefully
if Bing changes its markup.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(json.dumps({"error": f"Missing dependency: {e}. Run install.sh."}))
    sys.exit(1)


CACHE_DIR = Path.home() / ".cdhai-linkedin-skill" / "cache"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 cdhai-skill/0.4.1"
)

LEGAL_WARNING = (
    "WEB-SOURCED IMAGE — REQUIRES USAGE-RIGHTS VERIFICATION. "
    "Do not post on JHU / CDHAI / Carey accounts without confirming "
    "license terms or obtaining explicit permission from the rights holder."
)


def search_bing_images(query: str, max_results: int = 5) -> list:
    """Search Bing Images via HTML scraping. Returns list of result dicts."""
    url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    # Bing image result tiles contain a JSON-encoded `m` attribute on <a class="iusc">
    for a in soup.select("a.iusc"):
        m_json = a.get("m", "")
        if not m_json:
            continue
        try:
            m = json.loads(m_json)
        except Exception:
            continue

        image_url = m.get("murl", "")
        source_page = m.get("purl", "")
        if not image_url:
            continue

        results.append({
            "image_url": image_url,
            "thumbnail_url": m.get("turl", ""),
            "source_page": source_page,
            "title": m.get("t", "") or m.get("desc", ""),
            "width": m.get("w"),
            "height": m.get("h"),
            "_warning": LEGAL_WARNING,
        })
        if len(results) >= max_results:
            break

    return results


def search_duckduckgo_images(query: str, max_results: int = 5) -> list:
    """Fallback: DuckDuckGo image search.

    DDG's image search uses a vqd token + JSON API. We get the token from
    the HTML page, then call the API.
    """
    try:
        # Step 1: get vqd token
        r = requests.get(
            f"https://duckduckgo.com/?q={quote_plus(query)}&iax=images&ia=images",
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        r.raise_for_status()
        match = re.search(r'vqd="([^"]+)"', r.text) or re.search(r"vqd=([0-9-]+)", r.text)
        if not match:
            return []
        vqd = match.group(1)

        # Step 2: hit the image JSON endpoint
        api = f"https://duckduckgo.com/i.js?q={quote_plus(query)}&vqd={vqd}&o=json"
        r2 = requests.get(api, headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://duckduckgo.com/",
        }, timeout=15)
        r2.raise_for_status()
        data = r2.json()

        results = []
        for item in data.get("results", [])[:max_results]:
            results.append({
                "image_url": item.get("image", ""),
                "thumbnail_url": item.get("thumbnail", ""),
                "source_page": item.get("url", ""),
                "title": item.get("title", ""),
                "width": item.get("width"),
                "height": item.get("height"),
                "_warning": LEGAL_WARNING,
            })
        return results
    except Exception:
        return []


def download_image(image_url: str, dest: Path) -> bool:
    try:
        r = requests.get(image_url, headers={"User-Agent": USER_AGENT},
                         timeout=30, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Web image search (Tier 3 (c))")
    parser.add_argument("query", help="search query")
    parser.add_argument("--max", type=int, default=5, help="max results to return")
    parser.add_argument("--download", type=int, default=None,
                        help="download the Nth result (0-indexed) and cache it")
    parser.add_argument("--engine", choices=["bing", "ddg", "auto"], default="auto",
                        help="search backend")
    args = parser.parse_args()

    # Try Bing first (better JSON-embedded metadata), then DDG as fallback
    if args.engine in ("bing", "auto"):
        results = search_bing_images(args.query, args.max)
    else:
        results = []

    if not results and args.engine in ("ddg", "auto"):
        results = search_duckduckgo_images(args.query, args.max)

    if not results:
        print(json.dumps({
            "results": [],
            "error": "No results from any search backend.",
            "_warning": LEGAL_WARNING,
        }))
        return

    if args.download is not None:
        idx = args.download
        if idx >= len(results):
            print(json.dumps({"error": f"Index {idx} out of range; got {len(results)} results."}))
            sys.exit(1)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        chosen = results[idx]
        url = chosen["image_url"]
        h = hashlib.sha1(url.encode()).hexdigest()[:12]
        ext = ".jpg"
        if ".png" in url.lower(): ext = ".png"
        elif ".webp" in url.lower(): ext = ".webp"
        dest = CACHE_DIR / f"websearch_{h}{ext}"
        if download_image(url, dest):
            chosen["cached_path"] = str(dest)
            print(json.dumps(chosen, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({
                "error": f"Download failed for {url}",
                "source_page": chosen.get("source_page", ""),
            }))
            sys.exit(1)
    else:
        print(json.dumps({
            "query": args.query,
            "results": results,
            "_global_warning": LEGAL_WARNING,
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
