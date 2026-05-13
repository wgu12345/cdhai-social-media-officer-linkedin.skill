"""
unsplash_search.py — Search Unsplash for CC-licensed photos.

Used by the cdhai-social-media-officer-linkedin skill when the user's
folder has no images and they choose Unsplash as a fallback source.

Usage:
    python3 _helpers/unsplash_search.py "DC tech corridor healthcare AI"
    python3 _helpers/unsplash_search.py "Johns Hopkins campus" --per-page 5

Requires:
    ~/.cdhai-linkedin-skill/config.json with "unsplash_access_key" populated.

Returns: JSON to stdout with list of image candidates (URL, photographer,
attribution string). Skill consumes this and presents to user for selection.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".cdhai-linkedin-skill" / "config.json"
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


def load_key() -> str:
    if not CONFIG_PATH.exists():
        sys.stderr.write(
            f"Config not found at {CONFIG_PATH}. Run install.sh first.\n"
        )
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    key = config.get("unsplash_access_key", "").strip()

    if not key:
        sys.stderr.write(
            "Unsplash access key not configured in "
            f"{CONFIG_PATH}.\n"
            "Get a free key at https://unsplash.com/developers and paste\n"
            "it into the 'unsplash_access_key' field.\n"
        )
        sys.exit(2)

    return key


def search(query: str, per_page: int = 10, orientation: str = "landscape") -> list:
    try:
        import requests
    except ImportError:
        sys.stderr.write("requests not installed. Run install.sh.\n")
        sys.exit(1)

    key = load_key()

    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation,
        "content_filter": "high",
    }
    headers = {
        "Authorization": f"Client-ID {key}",
        "Accept-Version": "v1",
    }

    response = requests.get(UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = []
    for img in data.get("results", []):
        results.append({
            "id": img["id"],
            "description": img.get("alt_description") or img.get("description") or "",
            "url_regular": img["urls"]["regular"],
            "url_full": img["urls"]["full"],
            "url_thumb": img["urls"]["thumb"],
            "width": img["width"],
            "height": img["height"],
            "photographer_name": img["user"]["name"],
            "photographer_profile": img["user"]["links"]["html"],
            "unsplash_page": img["links"]["html"],
            "attribution": f"Photo by {img['user']['name']} on Unsplash",
        })

    return results


def download(image_url: str, output_path: Path) -> None:
    """Download a single image to disk."""
    try:
        import requests
    except ImportError:
        sys.stderr.write("requests not installed. Run install.sh.\n")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url, stream=True, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Saved {output_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", help="Search query (natural language)")
    ap.add_argument("--per-page", type=int, default=10, help="Number of results (default 10)")
    ap.add_argument("--orientation", default="landscape", choices=["landscape", "portrait", "squarish"])
    ap.add_argument("--download-to", type=Path, default=None, help="Optional: download all results to this directory")
    args = ap.parse_args()

    results = search(args.query, per_page=args.per_page, orientation=args.orientation)

    if args.download_to:
        for i, r in enumerate(results, 1):
            ext = ".jpg"
            filename = args.download_to / f"unsplash_{i:02d}_{r['id']}{ext}"
            download(r["url_regular"], filename)

    print(json.dumps(results, indent=2, ensure_ascii=False))
