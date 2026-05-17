#!/usr/bin/env python3
"""
validate_template.py — v0.4.3

Hard contract gate. Runs BEFORE any draft generation in Phase 1.

Exits 0  → template is acceptable, skill may proceed.
Exits 2  → template is missing required fields, skill MUST stop.
           A human-readable message is printed to stderr for Codex/the user.

This script is the enforcement layer for the "Word template required"
constraint declared in SKILL.md. SKILL.md instructions are soft; Codex
can rationalize around them. This script's exit code is hard — Codex
cannot pretend a non-zero exit code is zero.

Usage:
    python3 _helpers/validate_template.py <folder_path>
"""

import sys
import re
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("ERROR: python-docx not installed. Run: pip3 install python-docx",
          file=sys.stderr)
    sys.exit(3)

REQUIRED_FIELDS = [
    "Purpose",
    "Post Type",
    "Date",
    "Key Points",
    "Background",        # accepts "Background", "Background / Source Materials", etc.
    "Notes",             # accepts "Notes", "Notes for the writer", etc.
]


def find_content_docx(folder: Path) -> Path | None:
    """Return the most plausible content template, or None.

    Priority: anything ending in content.docx > anything with 'template' or
    'content' in the stem > first .docx file in the folder.
    """
    candidates = list(folder.rglob("*.docx"))
    if not candidates:
        return None
    # priority 1: literal content.docx
    for c in candidates:
        if c.name.lower() == "content.docx":
            return c
    # priority 2: template/content in name
    for c in candidates:
        if "template" in c.stem.lower() or "content" in c.stem.lower():
            return c
    # fallback: first docx
    return candidates[0]


def extract_all_text(doc_path: Path) -> str:
    """Pull every paragraph + table cell into one big lowercase string."""
    doc = Document(doc_path)
    chunks = []
    for p in doc.paragraphs:
        chunks.append(p.text)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                chunks.append(cell.text)
    return "\n".join(chunks).lower()


def field_present(text: str, field: str) -> bool:
    """A field is 'present' if its label appears followed by some content.

    We look for the label at the start of a line / heading / table cell
    boundary, then check there is non-trivial content after it on that
    same line or the next line.
    """
    pattern = re.compile(
        rf"(^|\n)\s*{re.escape(field.lower())}\b[:\-\s]*(.*)",
        re.IGNORECASE | re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        return False
    # require some content after the label (≥10 chars of body)
    tail = m.group(2).strip()
    if len(tail) >= 10:
        return True
    # or check the line below — find the position and look at next line
    next_chunk = text[m.end(): m.end() + 200].strip()
    return len(next_chunk) >= 10


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_template.py <folder_path>", file=sys.stderr)
        sys.exit(3)

    folder = Path(sys.argv[1]).expanduser().resolve()
    if not folder.is_dir():
        print(f"ERROR: folder not found: {folder}", file=sys.stderr)
        sys.exit(3)

    doc_path = find_content_docx(folder)
    if doc_path is None:
        print(
            "BLOCKED: No .docx content template found in the folder.\n"
            "\n"
            "This skill requires a filled Word template (content.docx) with "
            "these fields:\n"
            "  Purpose, Post Type, Date, Key Points, Background / Source "
            "Materials, Notes for the writer\n"
            "\n"
            "Download the blank template from _template/content_template.docx,\n"
            "fill it in, and re-run.",
            file=sys.stderr,
        )
        sys.exit(2)

    text = extract_all_text(doc_path)
    missing = [f for f in REQUIRED_FIELDS if not field_present(text, f)]

    if missing:
        print(
            f"BLOCKED: Template at {doc_path.name} is missing required "
            f"fields:\n"
            f"  {', '.join(missing)}\n"
            "\n"
            "This skill enforces a structured input as a hard contract.\n"
            "The text-only / sparse-prompt fallback was removed in v0.4.3 "
            "because it led to:\n"
            "  - hallucinated event details (slido polls, session names)\n"
            "  - skipped reviewer pass\n"
            "  - low-quality output\n"
            "\n"
            "Please fill the missing fields in content.docx (use "
            "_template/content_template.docx as a starting point), then "
            "re-run.\n"
            "\n"
            "Codex: do NOT attempt to bypass this check by inferring missing "
            "fields from agenda PDFs or other materials. Stop and ask the "
            "user to fill the template.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Success — print a compact line that build_docx can capture later
    print(f"OK: template validated at {doc_path.name}")
    print(f"Fields present: {', '.join(REQUIRED_FIELDS)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
