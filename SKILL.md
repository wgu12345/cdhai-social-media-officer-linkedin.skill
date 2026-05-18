---
name: cdhai-social-media-officer-linkedin
version: 0.4.4
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

## Contracts (v0.4.4)

Two mechanical contracts are enforced by helper scripts. Their behavior
in v0.4.4 is intentionally asymmetric — template input is soft because
real users sometimes have legitimately sparse fields; reviewer
independence is hard because the v0.4.2 team-member regression showed
quality collapses without it.

### 1. Template diagnostic — SOFT (v0.4.4 change vs v0.4.3)

`_helpers/validate_template.py` runs first, but **always exits 0**
unless the folder itself is unreadable. It classifies each of the six
template fields (Purpose, Post Type, Date, Key Points, Background /
Source Materials, Notes for the writer) as `filled`, `sparse`, or
`missing`, and writes the result to
`~/.cdhai-linkedin-skill/cache/template_validation.json`.

`sparse` means: present but with content shorter than 10 characters or
matching a placeholder like `NA`, `N/A`, `None`, `TBD`, `-`. This is
fine — users can write `NA` for fields that legitimately don't apply.

Phase 9 reads the validation JSON and surfaces the findings in
`before_you_post.docx` under (a) the Audit Log section and (b) the
Must-Verify section if any field was sparse or missing.

The skill does NOT halt on a sparse template. v0.4.3 did, and that
proved too brittle — see CHANGELOG for the trade-off.

### 2. Reviewer mandatory — HARD

After Phase 7 and before Phase 9, the reviewer sub-agent must run as
an independent Codex sub-agent and write a flag file at
`~/.cdhai-linkedin-skill/cache/reviewer_ran_<run_id>.flag`. Phase 9
begins by calling `_helpers/reviewer_check.py <run_id>`. If the flag
is missing, the skill halts.

In-line self-review in the writer's own turn is NOT a valid
substitute. This is the contract that prevents the v0.4.2 regression
(skipped reviewer → no quality checks → hallucinated content,
hashtag-pool violations, mis-identified photos, etc.).

If Codex finds itself reasoning about how to satisfy the user despite
a non-zero exit code from `reviewer_check.py`, that reasoning is
incorrect by definition — stop and surface the script's stderr to the
user instead.

### Other rules (markdown-only, not mechanically enforced)

- All intermediate `working_draft_*.md`, `post_manifest.json`,
  `report_data.json`, `image_manifest.jsonl`, and `contact_sheet_*.jpg`
  files stay in `~/.cdhai-linkedin-skill/cache/`. They are NEVER
  written to the user's project folder.
- Every `before_you_post.docx` must contain an "Audit Log" section
  recording which contracts passed, warned, or were bypassed.

---

# CDHAI Social Media Officer — LinkedIn (v0.4.4)

A draft generator for the Center for Digital Health and Artificial
Intelligence (CDHAI) at Johns Hopkins Carey Business School.

**v0.4.4 architecture**: this skill is designed to run in Codex App,
which is itself powered by GPT-5. All vision tasks, all language tasks,
and all judgment-based checks are performed by Codex directly — the
skill does NOT call out to a separate OpenAI API. Helpers exist only
for deterministic operations: PDF text extraction (`pypdf`), web HTML
scraping, image file building, Word document construction, template
validation diagnostic, and reviewer gate enforcement.

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

**Step 1a (template diagnostic):** call `python3 _helpers/validate_template.py "<folder>"`.

This script always exits 0 unless the folder is unreadable. It writes a
JSON report at `~/.cdhai-linkedin-skill/cache/template_validation.json`
with status `OK`, `WARN`, or `NO_TEMPLATE`, plus per-field
classification (`filled` / `sparse` / `missing`). Read this JSON and
remember the findings for Phase 9.

If status is `WARN` or `NO_TEMPLATE`, briefly tell the user which
fields are sparse or missing, and ask if they want to fill them
before continuing. If they say "go ahead" or similar, proceed; if they
say they'll fill them, wait. Either way, the validation JSON is
preserved for the final report.

**Do NOT halt the run** just because validation came back WARN.
v0.4.4 explicitly allows sparse fields; the report will record what
the AI inferred for them.

**Step 1b:** parse the folder.

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

6. **Parse the template**. Extract the structured fields. For fields that the validator flagged as sparse or missing, do the best inference you can from the supporting materials (agenda PDFs, photos, paper PDFs). Record every inferred value in the working state — Phase 9 will surface them in Must-Verify.

7. **Soft sanity checks** (not blocking):
   - `Post Type` ideally matches one of the nine in `_rules/content_types.md`. If not, ask the user once; if they reaffirm an unusual type, respect it.
   - `Key Points` ideally contains at least one item. If empty after inference, ASK the user — do not invent Key Points.

8. **No content type auto-detection.** The user picked it. Respect it.

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

### Step 8e — Phase 8 flag write (hard contract)

When the reviewer sub-agent returns SHIP (or returns CRITICALs and the
writer's 3-iteration revision loop concludes), the writer MUST run:

```bash
touch ~/.cdhai-linkedin-skill/cache/reviewer_ran_<run_id>.flag
```

This flag is the gate Phase 9 will check. Without it, output assembly
will refuse to write the final docx. If Codex skips the sub-agent and
does an in-line review instead, the flag will not exist, and the run
will halt at Phase 9.

---

## Phase 9 — Output assembly

**Step 9a (hard contract):** call `python3 _helpers/reviewer_check.py <run_id>` and check the exit code. If non-zero, print the helper's stderr verbatim and stop. Do NOT write `linkedin_post.docx` or `before_you_post.docx` until this passes.

Only continue if the check exited 0.

**Step 9b:** read `~/.cdhai-linkedin-skill/cache/template_validation.json` (written by Phase 1's diagnostic helper). Use its `summary_for_audit_log` and `summary_for_must_verify` fields when assembling `before_you_post.docx`.

**Step 9c:** produce the two deliverables, both `.docx`:

| File | Purpose |
|---|---|
| `linkedin_post.docx` | The post text with **inline embedded images**. Each Key Point's paragraph appears with its matched image right below. Hashtags at end. Copy-paste-ready for LinkedIn. |
| `before_you_post.docx` | Single merged report: legal-warning banner (if any web-sourced images), Audit Log, must-verify items, decisions, image picks with diversity check, quality checks, optional paper info, posting instructions. |

The `before_you_post.docx` MUST contain these sections in order:

1. **Legal-warning banner** (only if any web-sourced images are used; otherwise omitted)
2. **Audit Log (v0.4.4)** — A line for every contract:
   - Template diagnostic: PASS / WARN / NO_TEMPLATE (from `template_validation.json`; quote `summary_for_audit_log` verbatim)
   - Reviewer sub-agent: PASS (always PASS by the time we reach Phase 9, because reviewer_check would have halted otherwise)
   - Working-files location: PASS / LEAKED (with file list)
   - Memory file loaded: PASS / EMPTY (which file)
3. **Must-verify items** — facts and decisions the user must confirm. If template_validation.json has `summary_for_must_verify`, include it here verbatim at the top of the section.
4. **Decisions you should know** — choices the skill made
5. **Date verification** — Phase 2 output
6. **Image picks** — with diversity check
7. **Quality checks** — 9 reviewer checks with severities
8. **Paper info** (if applicable) — Phase 3 output
9. **Posting instructions**

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
- **Word document is the preferred input — v0.4.4 enforces template structure as a DIAGNOSTIC, not a hard gate.** `validate_template.py` writes findings to a JSON in cache; the skill proceeds and the final report surfaces sparse / missing fields. The v0.4.3 hard-block behavior was relaxed because legitimate uses (e.g., a user writing "NA" for "Notes for the writer") were being refused.
- **Reviewer sub-agent required — v0.4.4 enforces this mechanically via `_helpers/reviewer_check.py`.** This contract is HARD and not subject to user override. In-line self-review in the writer's own turn does not satisfy it. The reviewer must run as an independent Codex sub-agent with fresh context. The v0.4.2 team-member regression confirmed this gate's necessity.
- **No external OpenAI API key required.** Codex's native multimodal + LLM capabilities do all judgment work. Helpers are deterministic only.
- **Image generation goes through Codex's built-in `$imagegen` skill.** Uses your ChatGPT plan allocation, not API credits.
- **Web access required.** Tier 2 face identification fetches JHU / Carey pages; Tier 3 (c) searches the web.
- **Web-sourced images require manual usage-rights verification before posting.** Enforced by a prominent warning section in `before_you_post.docx` and CRITICAL reviewer flag.
- **Image processing is batched** (5 per batch) to avoid context window pressure.
- **Diversity constraints**: no single subject or scene type dominates the final picks.

---

## File map

```
cdhai-social-media-officer-linkedin.skill/
├── SKILL.md                          ← you are here
├── VERSION                           ← 0.4.4
├── README.md
├── CHANGELOG.md
├── install.sh                        ← seeds starter memory
├── skill.config.json
├── _rules/
│   ├── content_types.md
│   ├── linkedin_style.md
│   ├── asset_policy.md
│   ├── image_matching.md
│   ├── image_diversity.md
│   ├── paper_analysis.md
│   ├── date_factcheck.md
│   ├── inspiration_corpus.md
│   ├── brand_rules.md
│   ├── memory_policy.md
│   ├── core_rules.md
│   └── permission_policy.md
├── _template/
│   └── content_template.docx
├── _helpers/                         ← deterministic only
│   ├── build_docx.py
│   ├── face_compare.py
│   ├── pdf_paper_extract.py
│   ├── web_image_search.py
│   ├── validate_template.py          ← v0.4.4: SOFT diagnostic, exits 0
│   └── reviewer_check.py             ← v0.4.4: HARD gate, exits 2 if no flag
├── _memory_template/
│   ├── user_memory.md
│   └── memory_change_log.md
├── docs/
└── examples/
```
