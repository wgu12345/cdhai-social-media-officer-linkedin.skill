"""
dalle_generate.py — Generate an image via OpenAI DALL-E.

Used by the cdhai-social-media-officer-linkedin skill when the user's
folder has no images and they choose DALL-E as a fallback source.

Per JHU social-media guidelines, all DALL-E images must be flagged as
AI-generated in report.docx. The skill handles that disclosure step; this
helper just generates the image.

Usage:
    python3 _helpers/dalle_generate.py "DC tech corridor, healthcare AI, modern, professional"
    python3 _helpers/dalle_generate.py "Johns Hopkins campus aerial, sunny day" --size 1024x1024 --output ./images/

Requires:
    ~/.cdhai-linkedin-skill/config.json with "openai_api_key" populated.

Outputs: saves generated image to disk and writes the prompt + metadata
to a sidecar JSON file so the skill can disclose it correctly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path.home() / ".cdhai-linkedin-skill" / "config.json"
DALLE_API_URL = "https://api.openai.com/v1/images/generations"


def load_key() -> str:
    if not CONFIG_PATH.exists():
        sys.stderr.write(f"Config not found at {CONFIG_PATH}. Run install.sh first.\n")
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    key = config.get("openai_api_key", "").strip()

    if not key:
        sys.stderr.write(
            "OpenAI API key not configured in "
            f"{CONFIG_PATH}.\n"
            "Get one at https://platform.openai.com/api-keys and paste\n"
            "into the 'openai_api_key' field.\n"
        )
        sys.exit(2)

    return key


def generate(prompt: str, size: str = "1024x1024", model: str = "dall-e-3", quality: str = "standard") -> dict:
    try:
        import requests
    except ImportError:
        sys.stderr.write("requests not installed. Run install.sh.\n")
        sys.exit(1)

    key = load_key()

    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "response_format": "url",
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    response = requests.post(DALLE_API_URL, json=body, headers=headers, timeout=120)
    if response.status_code != 200:
        sys.stderr.write(f"DALL-E API error {response.status_code}: {response.text}\n")
        sys.exit(3)

    data = response.json()
    result = data["data"][0]

    return {
        "url": result["url"],
        "revised_prompt": result.get("revised_prompt", prompt),
        "original_prompt": prompt,
        "size": size,
        "model": model,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "ai_generated": True,
        "disclosure_required": True,
    }


def download(image_url: str, output_path: Path) -> None:
    try:
        import requests
    except ImportError:
        sys.stderr.write("requests not installed. Run install.sh.\n")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url, stream=True, timeout=120)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prompt", help="Image prompt (natural language)")
    ap.add_argument("--size", default="1024x1024", choices=["1024x1024", "1024x1792", "1792x1024"])
    ap.add_argument("--model", default="dall-e-3", choices=["dall-e-2", "dall-e-3"])
    ap.add_argument("--quality", default="standard", choices=["standard", "hd"])
    ap.add_argument("--output", type=Path, default=Path("./images_used"))
    args = ap.parse_args()

    print(f"Generating with prompt: {args.prompt}")
    metadata = generate(args.prompt, size=args.size, model=args.model, quality=args.quality)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    image_path = args.output / f"dalle_{timestamp}.png"
    sidecar_path = args.output / f"dalle_{timestamp}.json"

    download(metadata["url"], image_path)
    sidecar_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved {image_path}")
    print(f"Saved {sidecar_path}")
    print()
    print("REMINDER: This image is AI-generated. The skill must disclose")
    print("this in report.docx under 'AI-generated images used'.")
