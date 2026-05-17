---
name: cdhai-social-media-officer-linkedin
version: 0.4.2
description: |
  Generates a polished LinkedIn post draft from a folder containing a filled-in
  Word content template plus supporting materials (PDFs, images, research papers).
  Uses Codex's native multimodal capabilities for vision, paper analysis, and
  quality review. Helpers handle only deterministic work (web search, PDF
  text extraction, docx building). No external OpenAI API key required.
  Auto-invokes cdhai-content-reviewer as a sub-agent for independent quality
  review. Performs visual-to-semantic image matching against each Key Point
  with diversity constraints (no single subject dominates the picks).
trigger:
  - I want to draft a LinkedIn post
  - use cdhai-social-media-officer-linkedin
  - draft a CDHAI LinkedIn post
  - generate a LinkedIn post from my folder
  - write a LinkedIn post about
---

# CDHAI Social Media Officer — LinkedIn (v0.4.2)

A draft generator for the Center for Digital Health and Artificial
Intelligence (CDHAI) at Johns Hopkins Carey Business School.

**v0.4.2 architecture**: this skill is designed to run in Codex App,
which is itself powered by GPT-5. All vision tasks, all language tasks,
and all judgment-based checks are performed by Codex directly — the
skill does NOT call out to a separate OpenAI API. Helpers exist only
for deterministic operations: PDF text extraction (`pypdf`), web HTML
scraping, image file building, and Word document construction.

**Companion skill**: `cdhai-content-reviewer` runs automatically at the
end of every run, invoked as a **Codex sub-agent** for independent
context (fresh-eyes pass). The user invokes one skill; both run; one
merged report is produced.

---

## Phase 0 — Bootstrap

1. Verify `~/.cdhai-linkedin-skill/` exists. If not, run `install.sh` from the skill directory.
2. Check `VERSION` against the GitHub remote — warn if local version is behind.
3. Load `~/.cdhai-linkedin-skill/config.json`. The only optional key is `serpapi_key` (cleaner web search for Tier 2 face identification). All AI work is done by Codex; no API key required.
4. Detect user language from chat. Default English.

---

## Phase 1 — Read the user's folder

1. Locate the user's working folder (provided in the chat or via project context).
2. Read all files in `_rules/` — authoritative for this run.
3. Read `~/.cdhai-linkedin-skill/memory/user_memory.md` — accumulated user rules.
4. **Scan the folder for ALL file types — no priority order**:
   - **Word documents (`.docx`, `.doc`)** — primary structured content
   - **PDFs** — research papers, agendas, slide exports, conference programs
   - **Images** (`.jpg`, `.png`, `.heic`, etc.) — visual candidates for the post
   - **Text files** (`.txt`, `.md`) — supplementary notes

5. **Find the Content Template**: locate a Word document following `_template/content_template.docx` structure with these sections:
   - `Purpose`, `Post Type`, `Date`, `Key Points`, `Background / Source Materials`, `Notes for the writer`

6. **If no compliant Word template is found** → stop. Instruct the user to fill in `_template/content_template.docx` and re-run.

7. **Parse the template**. Extract the structured fields.

8. **Validate required fields**:
   - `Post Type` must be one of the nine listed in `_rules/content_types.md`. If missing or invalid → ask the user to pick.
   - `Date` must be present. If missing → ask.
   - `Key Points` must contain at least one item. If empty → stop and ask.
   - `Purpose` must be present. If missing → ask.

9. **No content type auto-detection.** The user picked it. Respect it.

---

## Phase 2 — Date fact-check

Detailed spec: `_rules/date_factcheck.md`.

Codex knows today's actual date from runtime. For every date-anchored
claim in the source materials:

1. **Compare** the user's Event Date against today's date.
2. **Compute** the natural-language reference for the post ("yesterday", "last week", "earlier this month", etc.).
3. **Cross-reference** against dates found in supporting PDFs. Mismatches → log as date conflicts, omit dates from draft until resolved.
4. **Flag temporal inconsistencies** (Post Type ↔ tense mismatches).
5. Log all date reasoning in the report under "Date verification".

---

## Phase 3 — Paper analysis (when applicable)

Detailed spec: `_rules/paper_analysis.md`.

If Post Type is `research_published` OR a research paper PDF is detected
in the folder:

### Step 3a — Extract text

```bash
python3 _helpers/pdf_paper_extract.py <paper.pdf>
```

This returns JSON with `first_two_pages` (where title/authors/abstract
typically live) and `full_text_chunks` (paragraph-bounded chunks of the
full text). **No LLM call inside the helper** — Codex analyzes the
returned text directly.

### Step 3b — Codex analyzes the extracted text

**You (Codex) read the extracted text and produce a structured paper
bundle.** Output ONLY this JSON, no other text:

```json
{
  "metadata": {
    "title": "string or null",
    "authors": [{"name": "string", "affiliation": "string or null"}],
    "abstract": "verbatim abstract or null",
    "keywords": ["..."],
    "venue": "journal / conference / 'Working paper' / null",
    "doi": "string or null",
    "publication_date": "YYYY-MM or YYYY-MM-DD or null",
    "page_count": <integer>
  },
  "substance": {
    "key_findings": [
      {"finding": "string", "source_chunk_index": <int>}
    ],
    "methodology_one_sentence": "...",
    "implications_one_sentence": "...",
    "limitations_one_sentence": "... or null",
    "audience_friendly_takeaway": "one paragraph"
  }
}
```

**Anti-hallucination contract** (hard):
- Every `finding` MUST trace to a specific chunk index from the helper output.
- Never strengthen the paper's claims (no "massive 12% improvement" if the paper says "average improvement of 12%").
- Never extend findings beyond their stated scope.
- If a field is genuinely absent, return `null`. Do not fabricate.

### Step 3c — Author identification

For each author, run:
```bash
python3 _helpers/face_compare.py --identify "<author name>"
```

This is the deterministic part (web search + headshot download). The
helper returns a cached reference photo path. Codex uses these reference
photos in Phase 5 Tier 2 (face comparison done natively by Codex looking
at both images, NOT via an external API call).

Tag each author as `faculty_internal` / `student_or_postdoc` / `external_collaborator`.

### Step 3d — Save the bundle

Save the bundle to `~/.cdhai-linkedin-skill/cache/paper_<run_id>.json`.

---

## Phase 4 — Image analysis (Tier 1: describe everything, batched)

For every image file in the folder + every image extracted from PDFs:

### Batched processing (mitigation #2)

Codex processes images in **batches of 5** to avoid context window
pressure and attention degradation:

For each batch of 5 images:
1. **Look at the 5 images directly** (Codex is multimodal native).
2. **Produce 5 entries** in the manifest, each strictly matching this JSON shape:

```json
{
  "path": "/absolute/path/to/image.jpg",
  "scene_summary": "1-2 sentence factual description",
  "people_count_approx": <integer>,
  "named_subjects_visible": [],
  "visible_text": ["banner text", "signage"],
  "setting": "indoor_podium | indoor_panel | indoor_classroom | indoor_lab | indoor_reception | indoor_office | outdoor_campus | outdoor_other | screenshot | document | unclear",
  "estimated_quality": "high | medium | low",
  "tags": ["short", "descriptive", "tags"]
}
```

3. **Append the batch** to `~/.cdhai-linkedin-skill/cache/image_manifest_<run_id>.jsonl` (one JSON per line).
4. **Summarize the batch's results in one line** to keep in context: e.g. "Batch 1/3: 3 podium shots of Gordon, 1 panel shot of Ritu, 1 audience wide shot."
5. **Discard the detailed manifest from active context** and move to the next batch. The manifest file on disk is the source of truth.

**Hard rules for the JSON output:**
- Be factual; do not interpret or speculate.
- `named_subjects_visible` only contains names IF you can identify them with high confidence (e.g., visible name tag, recognized from reference photos cached earlier). If unsure, leave empty.
- `visible_text` includes ONLY text actually legible in the image.
- Reply with valid JSON per image, one per line. NO prose before, between, or after the JSON entries.

---

## Phase 5 — Key Point ↔ Image matching

### Step 5a — Per-Key-Point semantic matching (Tier 1)

For each Key Point in the template, Codex:

1. Constructs a target description from the Key Point text.
2. Reads the image manifest from disk.
3. Scores every image's manifest entry against the target on:
   - Topic match (scene type fits?)
   - Setting match (institutional signage?)
   - Object match (whiteboard, slides, named subjects, etc.)
4. Scores 0-1. ≥0.7 = strong match. 0.4-0.7 = partial. <0.4 = unrelated.

### Step 5b — Specific person identification (Tier 2)

If a Key Point names a specific person AND no strong Tier 1 match exists:

1. Run the identify helper:
   ```bash
   python3 _helpers/face_compare.py --identify "<Full Name>"
   ```
   This is deterministic web search + headshot download. Returns cached reference path.

2. **Codex directly compares the reference photo against each candidate image** by looking at both. No API call. Output:
   ```json
   {
     "candidate_path": "/path/to/candidate.jpg",
     "reference_path": "/path/to/reference.jpg",
     "same_person_confidence": <0.0 to 1.0>,
     "justification": "one short sentence"
   }
   ```

3. Decide per Key Point:
   - **≥0.8** → high-confidence match → assign + note "Identified as <name> via web reference comparison" in the report.
   - **0.5-0.8** → possible match → assign tentatively + flag "verify before posting".
   - **<0.5** → fall through to Tier 3.

### Step 5c — Diversity check (NEW in v0.4.2)

Detailed spec: `_rules/image_diversity.md`.

After per-Key-Point matching produces tentative assignments:

1. **Tally subjects** (named people across all picks).
2. **Tally scene types**.
3. **Enforce caps**: no single named person in more than 2 picks (out of 5 — scales for larger sets); no single scene type in more than 2 picks.
4. **If violated**:
   - Keep the top-confidence picks for the over-represented subject/scene
   - Release the lower-confidence picks
   - Re-match the released Key Points using alternative candidates
   - If no alternative scores ≥ 0.5 → trigger Tier 3 (Phase 6) for that Key Point.

The goal: **every Key Point gets an image AND visual variety is preserved.**
Gordon doesn't take 3 of 5 slots just because he's in 8 of 13 photos.

---

## Phase 6 — Missing-image fallback (Tier 3)

For any Key Point without a matched image (Tier 1 < 0.4 AND Tier 2 <
0.5, OR released by Phase 5c diversification), the skill consults the
user. Verbatim prompt:

```
The Key Point "<exact text>" has no matching image in your folder.

Pick one:
(a) Provide your own image — I'll wait, then re-run.  [RECOMMENDED]
(b) Generate with Codex's built-in $imagegen skill.
    (AI-generated; flagged in report.)
    Suggested prompt: <auto-generated prompt>
(c) Search the web for an image.
    ⚠ WEB-SOURCED IMAGES REQUIRE MANUAL USAGE-RIGHTS VERIFICATION
    BEFORE POSTING.
    Suggested keywords: <auto-generated keywords>
(d) Skip this Key Point's visual anchor.
```

Behavior per choice:

- **(a)** → polite exit, user re-runs.
- **(b)** → **invoke Codex's built-in `$imagegen` skill** directly (the `image_gen` native tool, which uses your ChatGPT plan, NOT an API key). Save output to `~/.cdhai-linkedin-skill/cache/imagegen_<hash>.png`. Mark `source: "codex_imagegen"`, add to `ai_generated_disclosures`.
- **(c)** → run `python3 _helpers/web_image_search.py "<keywords>" --max 5`, show candidates with titles + source pages, user picks by index, run `--download <N>`. Mark `source: "web_search"`. **Triggers the prominent legal warning section at the top of `before_you_post.docx`** and a CRITICAL reviewer flag until user confirms usage rights.
- **(d)** → record the skip.

**Output target**: at minimum **5 distinct images** in the final draft.

---

## Phase 7 — Content generation

Generate ONE LinkedIn post draft (markdown internally; converted to docx
in Phase 9). Inputs:

- Parsed content template
- Paper bundle (if applicable) from Phase 3
- Image manifest with Key Point assignments
- `_rules/inspiration_corpus.md`, `_rules/linkedin_style.md`, `_rules/brand_rules.md`
- `user_memory.md` (highest precedence)

**Generation rules (hard):**

1. **Every Key Point MUST appear in the post.** If a Key Point cannot be naturally worked in → stop and ask the user.
2. **Every body paragraph MUST have a specific anchor**: a named person with full name + title (first mention), or a named session / paper / publication, or a specific number with source, or a specific quote with source. Otherwise the reviewer flags as "too generic" and rejects.
3. **Polish only, never invent.** Verify-by-Googling test: if a thoughtful reader would Google a claim, the claim must be sourced or asked.
4. **Voice**: `inspiration_corpus.md`. Open with a question, a concrete moment, a number, or a direct quote.
5. **Length**: per Post Type, per `content_types.md`.
6. **Hashtags**: 3-5 at end, default 4. Per `brand_rules.md`.

### Phase 7b — Ask-when-missing

Before finalizing, scan the draft for claims a thoughtful reader would
have to Google. For each:
- Source-of-truth in input materials? → cite, proceed.
- Not in input materials? → **ASK the user**.

---

## Phase 8 — Auto-invoke reviewer (as Codex sub-agent)

Mitigation #1: the reviewer runs in a **Codex sub-agent**, not as a
continuation of the current Codex turn. This gives the reviewer a fresh
context — independent eyes, no bias toward approving the writer's own
draft.

### Step 8a — Save inputs for the reviewer

1. Save the working draft to `~/.cdhai-linkedin-skill/cache/working_draft_<run_id>.md`.
2. Ensure the image manifest, Key Points, and paper bundle (if any) are saved to cache.

### Step 8b — Invoke sub-agent

Use Codex's sub-agent mechanism (the `@subagent` or equivalent), passing:

```
Sub-agent task: cdhai-content-reviewer

Inputs:
  draft_path: ~/.cdhai-linkedin-skill/cache/working_draft_<run_id>.md
  folder_path: <user's folder>
  content_template: <path to content.docx>
  image_manifest: ~/.cdhai-linkedin-skill/cache/image_manifest_<run_id>.jsonl
  paper_bundle: <optional path>
  key_points: [list]

Return structured JSON findings (per cdhai-content-reviewer's SKILL.md).
```

The sub-agent reads `cdhai-content-reviewer.skill/SKILL.md`, runs the 9
checks, and returns structured JSON. Because the sub-agent starts with a
fresh context, it does NOT see the writer's intermediate reasoning — only
the final draft, like a real second reviewer would.

### Step 8c — Handle reviewer findings

1. Parse the sub-agent's JSON response.
2. **If `summary.ship_recommendation == "BLOCK"`** (any CRITICAL):
   - Revise the draft based on the CRITICAL items.
   - Re-invoke the reviewer sub-agent on the revised draft.
   - Maximum 3 revision loops.
3. **If `summary.ship_recommendation == "REVISE"`** (no critical, 3+ warnings):
   - Address WARNING items where reasonable.
   - Optionally re-invoke reviewer for a second pass.
4. **If `summary.ship_recommendation == "SHIP"`**: proceed.

After 3 revision loops, output the latest draft and surface all
unresolved CRITICALs in the report. The user makes the final call.

### Step 8d — Merge findings into the report

The reviewer's findings get merged into the writer's
`before_you_post.docx`. The reviewer does NOT write its own file in
auto mode.

---

## Phase 9 — Output assembly

Two deliverables, both `.docx`:

| File | Purpose |
|---|---|
| `linkedin_post.docx` | The post text with **inline embedded images**. Each Key Point's paragraph appears with its matched image right below. Hashtags at end. Copy-paste-ready for LinkedIn. |
| `before_you_post.docx` | Single merged report: legal-warning banner (if any web-sourced images), must-verify items, decisions, image picks with diversity check, quality checks, optional paper info, posting instructions. |

Conversion handled by `_helpers/build_docx.py` (deterministic — python-docx).

**No `.md` files in output.** All working markdown stays in cache.

**Optional PDF export**: if the user asks, the skill also produces `linkedin_post.pdf` via `soffice` or `weasyprint`.

---

## Phase 10 — Memory and feedback

Three-path per `_rules/memory_policy.md`:

1. **Decline** — discard, no record.
2. **This run only** — apply, log in `before_you_post.docx`, no memory write.
3. **Save as permanent rule** — apply, translate informal feedback to formal rule, append to `user_memory.md`, log in `memory_change_log.md`.

Codex always **asks which path** before writing to memory.

---

## Constraints

- **English only.** Multilingual on the v0.6 roadmap.
- **No direct posting.** Drafts only. Human review required.
- **Word document required as primary input.** Text-only and markdown-only inputs are rejected with an instructive error message.
- **No external OpenAI API key required.** v0.4.2 uses Codex's native multimodal + LLM capabilities. Helpers are deterministic only.
- **Image generation goes through Codex's built-in `$imagegen` skill.** Uses your ChatGPT plan allocation, not API credits.
- **Web access required.** Tier 2 face identification fetches JHU / Carey pages; Tier 3 (c) searches the web.
- **Web-sourced images require manual usage-rights verification before posting.** Enforced by a prominent warning section in `before_you_post.docx` and CRITICAL reviewer flag.
- **Reviewer must run as a Codex sub-agent** for independent context. Never in-line in the writer's turn.
- **Image processing is batched** (5 per batch) to avoid context window pressure.
- **Diversity constraints**: no single subject or scene type dominates the final picks.

---

## File map

```
cdhai-social-media-officer-linkedin.skill/
├── SKILL.md                          ← you are here
├── VERSION                           ← 0.4.2
├── README.md
├── install.sh
├── skill.config.json
├── _rules/
│   ├── content_types.md              ← 9 types, lengths, tones
│   ├── linkedin_style.md             ← hype density, hook patterns
│   ├── asset_policy.md               ← high-level image routing
│   ├── image_matching.md             ← Tier 1/2/3 spec
│   ├── image_diversity.md            ← NEW v0.4.2: per-subject + per-scene caps
│   ├── paper_analysis.md             ← Phase 3 spec
│   ├── date_factcheck.md             ← Phase 2 spec
│   ├── inspiration_corpus.md         ← peer institution voice
│   ├── brand_rules.md                ← naming, hashtags, capitalization
│   ├── memory_policy.md              ← three-path memory
│   ├── core_rules.md                 ← never invent, never auto-post
│   └── permission_policy.md
├── _template/
│   └── content_template.docx         ← Word template
├── _helpers/                         ← DETERMINISTIC ONLY in v0.4.2
│   ├── build_docx.py                 ← python-docx post + report builder
│   ├── face_compare.py               ← --identify only (web search + download)
│   ├── pdf_paper_extract.py          ← pypdf text only (Codex analyzes the text)
│   └── web_image_search.py           ← Bing/DDG scraping (no API key)
├── _memory_template/
│   ├── user_memory.md
│   └── memory_change_log.md
├── docs/
│   └── team-guide.md
└── examples/
    └── filled-template-example/
```
