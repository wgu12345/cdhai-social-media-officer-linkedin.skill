# Asset Policy

How the skill handles images, and what happens when matching to Key Points
fails. This file is the high-level routing; the detailed Tier 1/2/3 spec
lives in `image_matching.md`.

---

## Folder convention (v0.4.1)

The skill expects:

```
user_folder/
├── content.docx (or content.doc)     ← required, filled-in template
├── (any number of PDFs)               ← papers, agendas, slides
├── (any number of images)             ← user-provided visual candidates
└── (any other supporting docs)        ← txt, md, second docx, etc.
```

**No required subfolder structure.** Images can be at the folder root or
in a subfolder. The skill scans recursively.

**No file-type priority.** Every file contributes:
- `.docx` carries the structured content (template fields).
- `.pdf` is read for text content AND scanned for embedded images. Research papers trigger the full Phase 3 analysis.
- Images are visual candidates for Key Point matching.
- `.txt` and `.md` are supplementary notes.

---

## Phase 2 — Image acquisition flow

1. **Collect all images** in the folder (root + subfolders, recursive).
2. **Extract images from PDFs** in the folder via `pypdf` + image embedding extraction.
3. **Tier 1 + Tier 2 matching** runs on every image against every Key Point (`image_matching.md`).
4. **For any Key Point with no match**, run Tier 3 fallback (consult user).
5. **Verify total image count ≥ 5**. If fewer → prompt user for more.

---

## Tier 3 fallback (v0.4.1)

When a Key Point has no matched image, ask the user:

```
The Key Point "<exact text>" has no matching image in your folder.

Pick one:
(a) Provide your own image — I'll wait, then re-run.  [RECOMMENDED]
(b) Generate with Codex's built-in $imagegen skill.
    (AI-generated; flagged in report.)
(c) Search the web for an image.
    ⚠️ WEB-SOURCED IMAGES REQUIRE MANUAL USAGE-RIGHTS VERIFICATION
    BEFORE POSTING.
(d) Skip this Key Point's visual anchor.
```

### Implementation per choice

**Choice (b) — Codex `$imagegen`**

Use the built-in tool, not our own API call. The agent invokes `image_gen`
natively. Save the output to `~/.cdhai-linkedin-skill/cache/imagegen_<hash>.png`
and mark as AI-generated in the manifest.

**Choice (c) — web image search**

Helper: `_helpers/web_image_search.py "<keywords>" --max 5`
- Scrapes Bing Images (DDG fallback). No API key required.
- Returns 5 candidates with image_url, source_page, title.
- User picks by index; skill downloads via `--download N`.
- **Every web-sourced image** triggers the legal warning section in `before_you_post.docx`.

---

## What lives where

| Storage | Lifetime | Purpose |
|---|---|---|
| User's folder | Permanent | Original images user provides |
| `~/.cdhai-linkedin-skill/cache/imagegen_*` | 30 days | `$imagegen` results |
| `~/.cdhai-linkedin-skill/cache/websearch_*` | 30 days | Web-search results |
| `~/.cdhai-linkedin-skill/cache/reference_*` | 90 days | Tier 2 reference faces |
| `~/.cdhai-linkedin-skill/cache/working_draft_*` | Until next run | In-progress drafts |

Cache is cleaned manually if needed.

---

## Hard rules

- **Never silently proceed with fewer than 5 images** unless the user explicitly says "yes I want a low-image post".
- **Never substitute a missing-person image with a generic stock photo without asking.** Stock for an unknown speaker is misleading.
- **Never re-encode, crop, or watermark user-provided images** for the embedded copies in `linkedin_post.docx`. Show them as uploaded.
- **Tier 2 face comparison requires user-provided face reference (web-fetched) for the named person.** Without a reference, fall through to Tier 1 description match.
- **All AI-generated images appear in the "AI-generated images" section of `before_you_post.docx`**, with the prompt that produced them.
- **All web-sourced images appear in the prominent "Web-sourced images — verify usage rights" section** at the top of `before_you_post.docx`. The reviewer's `image_match` check flags any web image lacking explicit usage-rights verification.
- **Never use a web-sourced image without surfacing the legal warning.** This is the #1 compliance rule in v0.4.1. JHU social media is a regulated channel; copyright exposure is institutional risk.

---

## Removed in v0.4.1

- **Unsplash API integration.** Helper deleted. Config key removed.
- **DALL-E direct API call helper.** Codex's built-in `$imagegen` replaces it; uses the user's existing ChatGPT plan allocation instead of API credits.
- **`images_used/` subfolder.** Images are embedded inline in `linkedin_post.docx`.
- **The "top 10 ranked, user picks 1-3" pattern.** Replaced by "every Key Point gets an image, minimum 5 total."
- **Watermarking / branding overlay on user images.** Complex, low value, risked altering branded photos the user already crafted.
