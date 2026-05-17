#!/usr/bin/env python3
"""
Research paper PDF text extraction.

Usage:
    python3 pdf_paper_extract.py <paper.pdf>

Extracts raw text from a PDF using pypdf. Returns JSON with:
  - page count
  - first two pages (where title/authors/abstract typically live)
  - all text chunks (split on paragraph boundaries, ~12k chars each)

The structured analysis (title, authors, key findings, etc.) is done by
Codex itself, reading the text returned here. This helper only does the
deterministic part: bytes → text.

NO OPENAI_API_KEY REQUIRED in v0.4.2 — Codex analyzes text directly.
"""
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError as e:
    print(json.dumps({"error": f"Missing pypdf: {e}. Run install.sh."}))
    sys.exit(1)


MAX_CHARS_PER_CHUNK = 12000


def extract_raw_text(pdf_path: Path) -> tuple:
    """Return (full_text, page_count, first_two_pages)."""
    reader = PdfReader(str(pdf_path))
    full = []
    first_two = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        full.append(text)
        if i < 2:
            first_two.append(text)
    return "\n\n".join(full), len(reader.pages), "\n\n".join(first_two)


def chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list:
    """Split long text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks, current, cur_len = [], [], 0
    for p in paragraphs:
        if cur_len + len(p) > max_chars and current:
            chunks.append("\n\n".join(current))
            current, cur_len = [p], len(p)
        else:
            current.append(p)
            cur_len += len(p)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def detect_paper_signals(first_two: str) -> dict:
    """Heuristic signals that this is a research paper (for SKILL.md decision logic)."""
    text_lower = first_two.lower()
    return {
        "has_abstract_header": bool(re.search(r"\babstract\b", text_lower)),
        "has_keywords_header": bool(re.search(r"\bkeywords?\s*[:：]", text_lower)),
        "has_doi": bool(re.search(r"\bdoi[:\s]*10\.", first_two, re.IGNORECASE)),
        "has_university_in_first_page": any(
            w in text_lower for w in ["university", "college", "institute", "hopkins"]
        ),
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: pdf_paper_extract.py <paper.pdf>", file=sys.stderr)
        sys.exit(2)

    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print(json.dumps({"error": f"File not found: {pdf}"}))
        sys.exit(1)

    full_text, page_count, first_two = extract_raw_text(pdf)
    chunks = chunk_text(full_text)
    signals = detect_paper_signals(first_two)

    out = {
        "_meta": {
            "path": str(pdf),
            "filename": pdf.name,
            "page_count": page_count,
            "chunk_count": len(chunks),
            "is_likely_research_paper": (
                signals["has_abstract_header"]
                and signals["has_university_in_first_page"]
            ),
            "signals": signals,
        },
        "first_two_pages": first_two,
        "full_text_chunks": chunks,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
