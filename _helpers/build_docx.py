"""
build_docx.py — Convert post content (markdown) + images into a clean .docx file.

Used by the CDHAI LinkedIn skill and reviewer skill to produce Word output
that non-technical users (Jennifer, MarComm) can open directly.

Why Word, not Markdown:
- Non-tech users can't easily open .md files
- Word handles inline images natively (MD does not unless rendered)
- LinkedIn copy-paste still works fine from Word (select-all → copy → paste)

Usage:
    python3 _helpers/build_docx.py <input.md> <output.docx> [--images img1.jpg ...]
    python3 _helpers/build_docx.py post.md post.docx --images images_used/banner.jpg

Dependencies:
    pip install python-docx Pillow --break-system-packages
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    sys.stderr.write(
        "python-docx not installed. Run:\n"
        "  pip install python-docx Pillow --break-system-packages\n"
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Markdown parsing (minimal — covers what our templates emit)
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
HR_RE = re.compile(r"^-{3,}\s*$")
SEVERITY_RE = re.compile(r"^\s*(CRITICAL|WARNING|SUGGESTION)\b[:.]?\s*(.*)$", re.IGNORECASE)


def parse_blocks(text: str):
    """Tokenize markdown into blocks: ('h1'|'h2'|'h3'|'bullets'|'numbers'|'p'|'hr'|'blank', content)."""
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.strip() == "":
            blocks.append(("blank", ""))
            i += 1
            continue

        if HR_RE.match(line):
            blocks.append(("hr", ""))
            i += 1
            continue

        h = HEADING_RE.match(line)
        if h:
            level = len(h.group(1))
            blocks.append((f"h{level}", h.group(2).strip()))
            i += 1
            continue

        if BULLET_RE.match(line):
            bullets = []
            while i < len(lines) and BULLET_RE.match(lines[i]):
                bullets.append(BULLET_RE.match(lines[i]).group(1))
                i += 1
            blocks.append(("bullets", bullets))
            continue

        if NUMBERED_RE.match(line):
            items = []
            while i < len(lines) and NUMBERED_RE.match(lines[i]):
                items.append(NUMBERED_RE.match(lines[i]).group(1))
                i += 1
            blocks.append(("numbers", items))
            continue

        # Paragraph: collect until blank or new block element
        para = [line]
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "":
                break
            if HEADING_RE.match(nxt) or BULLET_RE.match(nxt) or NUMBERED_RE.match(nxt) or HR_RE.match(nxt):
                break
            para.append(nxt)
            j += 1
        blocks.append(("p", " ".join(para).strip()))
        i = j

    return blocks


# ---------------------------------------------------------------------------
# Inline formatting (**bold**, *italic*, `code`)
# ---------------------------------------------------------------------------

INLINE_RE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")

def render_inline(paragraph, text: str):
    parts = INLINE_RE.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("*") and part.endswith("*"):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            r.font.name = "Consolas"
        else:
            paragraph.add_run(part)


def render_inline_colored(paragraph, text: str, color_rgb):
    """Same as render_inline but everything gets a uniform color (for severity items)."""
    parts = INLINE_RE.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("*") and part.endswith("*"):
            r = paragraph.add_run(part[1:-1])
            r.italic = True
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            r.font.name = "Consolas"
        else:
            r = paragraph.add_run(part)
        r.font.color.rgb = color_rgb


# ---------------------------------------------------------------------------
# Document building
# ---------------------------------------------------------------------------

SEVERITY_COLOR = {
    "critical": RGBColor(0xC0, 0x39, 0x2B),  # red
    "warning":  RGBColor(0xC8, 0x76, 0x1A),  # amber
    "suggestion": RGBColor(0x59, 0x59, 0x59),  # gray
}


def build(input_md: Path, output_docx: Path, image_paths=None):
    text = input_md.read_text(encoding="utf-8")
    doc = Document()

    # Base font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    blocks = parse_blocks(text)

    for kind, content in blocks:
        if kind == "h1":
            doc.add_heading(content, level=1)
        elif kind == "h2":
            doc.add_heading(content, level=2)
        elif kind == "h3":
            doc.add_heading(content, level=3)
        elif kind == "bullets":
            for b in content:
                p = doc.add_paragraph(style="List Bullet")
                sev = SEVERITY_RE.match(b)
                if sev:
                    color = SEVERITY_COLOR.get(sev.group(1).lower())
                    label = doc.paragraphs[-1].add_run(f"{sev.group(1).upper()}: ")
                    label.bold = True
                    if color is not None:
                        label.font.color.rgb = color
                    render_inline_colored(p, sev.group(2), color) if color else render_inline(p, sev.group(2))
                else:
                    render_inline(p, b)
        elif kind == "numbers":
            for item in content:
                p = doc.add_paragraph(style="List Number")
                render_inline(p, item)
        elif kind == "p":
            p = doc.add_paragraph()
            render_inline(p, content)
        elif kind == "blank":
            doc.add_paragraph()
        elif kind == "hr":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run("—" * 30)

    # Append images at the end, embedded inline
    if image_paths:
        valid = [Path(p) for p in image_paths if Path(p).exists()]
        if valid:
            doc.add_heading("Images", level=2)
            for img_path in valid:
                try:
                    doc.add_picture(str(img_path), width=Inches(5.5))
                    caption = doc.add_paragraph()
                    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r = caption.add_run(img_path.name)
                    r.italic = True
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
                except Exception as e:
                    p = doc.add_paragraph(f"[Could not embed image {img_path.name}: {e}]")
                    p.runs[0].italic = True

    doc.save(str(output_docx))
    print(f"Wrote {output_docx}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_md", type=Path, help="Input markdown file")
    ap.add_argument("output_docx", type=Path, help="Output .docx path")
    ap.add_argument("--images", nargs="*", default=[], help="Optional images to embed")
    args = ap.parse_args()

    if not args.input_md.exists():
        sys.stderr.write(f"Input not found: {args.input_md}\n")
        sys.exit(1)

    build(args.input_md, args.output_docx, args.images)
