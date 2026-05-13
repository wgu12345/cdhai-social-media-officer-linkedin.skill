---
name: cdhai-social-media-officer-linkedin
version: 0.3.0
description: |
  Generates a polished LinkedIn post draft from a folder of CDHAI / Carey
  source materials (event recap, research, faculty talk, grant announcement,
  etc.). Produces Word output ready for human review and copy-paste to
  LinkedIn. Designed for non-technical users (MarComm, Jennifer, Upasana)
  via Codex App; CLI route available for power users.
trigger:
  - I want to draft a LinkedIn post
  - use cdhai-social-media-officer-linkedin
  - generate a LinkedIn draft
  - write a LinkedIn post about
---

# CDHAI Social Media Officer — LinkedIn

A single-skill draft generator for the Center for Digital Health and
Artificial Intelligence (CDHAI) at Johns Hopkins Carey Business School.

Companion skill: **cdhai-content-reviewer** — runs after this skill to
flag typos, brand inconsistencies, hype density, and items needing human
verification. The two skills are designed to work together.

---

## Phase 0 — Bootstrap

Run once on first invocation per machine:

1. Verify `~/.cdhai-linkedin-skill/` exists. If not, run `install.sh`.
2. Check `VERSION` against `https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill/blob/main/VERSION` — warn if local version is behind.
3. Load `~/.cdhai-linkedin-skill/config.json` for API keys (Unsplash, DALL-E).
   - If keys are missing, note in report and skip those asset sources.
4. Detect user language from chat. Default English.

---

## Phase 1 — Read inputs and detect content type

1. Locate the user's working folder (provided in the chat or via project context).
2. Read all files in `_rules/` — these are authoritative for this run.
3. Read `~/.cdhai-linkedin-skill/memory/user_memory.md` — accumulated user rules.
4. Read the main content file: priority order `content.md` → `content.txt` → `content.docx` → `content.pdf`.
5. **Detect content_type** using rules in `_rules/content_types.md`.
   - Compute confidence per candidate type
   - If top type ≥70% confident → use it
   - If top type <70% OR top two within 10% → **ask the user** which fits
   - Acceptable types: `event_recap`, `upcoming_event`, `faculty_presentation`, `research_published`, `thought_leadership`, `awards_grants`, `people_announcement`, `partnership_announcement`, `general`
6. Set `tone` to the default for the detected `content_type` (see `_rules/content_types.md`). User can override in chat.
7. Set `target_length` to the chars target for the detected type.

---

## Phase 2 — Asset acquisition

Follow the flow in `_rules/asset_policy.md`:

1. Check `images/` folder
2. Try extraction from PDF/DOCX content
3. If still none → **ask user** for: Unsplash search / DALL-E generation / text-only
4. Never silently proceed without consulting user when images are absent

Helpers available:
- `_helpers/unsplash_search.py <keywords>` — CC-licensed photo search
- `_helpers/dalle_generate.py <prompt>` — DALL-E image generation
- Both require API keys in `~/.cdhai-linkedin-skill/config.json`

---

## Phase 3 — Style extraction (optional)

If user provided `style_reference.{txt,html,pdf}`:

1. If URL is provided as plain text → fetch and parse
2. If fetch returns 403 (Carey blocks bots) → **instruct user** to download as HTML or PDF; don't silently fail
3. Extract: palette signals, typography family, structural rhythm
4. Save extracted profile to `~/.cdhai-linkedin-skill/cache/style_profile_<hash>.json`
5. Pass profile to Phase 4

If not provided, proceed without style extraction.

---

## Phase 4 — Content generation

Generate ONE LinkedIn post draft (not two; see `content_types.md` for why
length is automatic, not a user choice up-front).

Inputs to this phase:
- Main content file (parsed)
- `_rules/inspiration_corpus.md` — peer institution voice
- `_rules/linkedin_style.md` — what to prefer, what to use sparingly
- `_rules/brand_rules.md` — naming, capitalization, hashtag policy
- `user_memory.md` — accumulated user rules (highest precedence)
- Detected content_type, tone, target_length

Generation principles:

- **Polish only, never invent.** If a fact isn't in the input → either omit
  or ask the user (see Phase 4b).
- **Match the inspiration corpus voice** (described in `inspiration_corpus.md`).
- **No banned words** — see `linkedin_style.md` for the density-based judgment that replaces a banlist.
- Hashtags at end, 3-5 with default 4, composition per `brand_rules.md`.
- Length: hit the target naturally based on input richness. Don't pad. Don't truncate.

### Phase 4b — Ask-when-missing

Before finalizing, scan the draft for any claim that a thoughtful reader
would have to Google to verify. For each:

- Is the source of truth in the input materials? → cite, proceed.
- Not in input materials? → **ASK the user**.

Categories that commonly trigger this:
- Name spelling (especially transliteration variants — Aggarwal vs Agarwal)
- Name completeness (first, last, title, role)
- Date anchoring ("yesterday" without anchor date)
- Location specificity ("at Hopkins" — which campus?)
- Numeric claims without source ("60% improvement" with no citation)
- Attribution ambiguity ("the team said X" — which team?)
- Acronym not expanded on first use

This is a principle, not a checklist. Apply the verify-by-Googling test.

---

## Phase 5 — Visual layout planning

Rank the images Codex has available (uploaded + extracted + searched + generated):

1. Semantic match to post content (image of the keynote speaker if post is about that keynote)
2. Source priority: user-provided > PDF-extracted > Unsplash > DALL-E
3. Resolution (≥1200px wide preferred)
4. Recency

**Picking rule** (see `asset_policy.md`):
- Total images < 10 → show all, ranked
- Total images ≥ 10 → pick top 10, ranked

The report.docx lists the ranking with a one-line reason per image. **User
makes the final pick.** Don't pre-decide 1-3 for them.

---

## Phase 6 — Asset processing

For each image the user might pick:

- Resize to LinkedIn-friendly dimensions per `brand_rules.md`:
  - Banner: 1200×627 (1.91:1)
  - Inline/square: 1080×1080 (1:1)
- Apply Carey logo watermark for non-CDHAI photos (15% opacity, bottom-right)
- Save processed images to `images_used/` next to the draft

The user opens `images_used/` locally to preview before publishing.

---

## Phase 7 — Review pass (handoff to reviewer skill)

After this skill completes Phase 6:

1. Save all output files to the user's working folder
2. Invoke `cdhai-content-reviewer` skill with the working folder as input
3. Reviewer produces `review_report.docx`
4. Reviewer findings (counts of critical / warning / suggestion) appear in
   our own `report.docx` summary section

Reviewer checks:
- Typos and grammar
- Brand consistency (naming, capitalization, hyphenation)
- Factual flags — uncited numbers, dates, names → flagged for human verification
- Hype density (per `linkedin_style.md` rule, not a banlist)
- Severity levels: critical / warning / suggestion

---

## Phase 8 — Output assembly

Working markdown is converted to Word using `_helpers/build_docx.py`. All
deliverables are `.docx` so non-technical users can open them directly.

**Output files** (in the user's working folder):

| File | Purpose |
|---|---|
| `linkedin_post.docx` | The primary deliverable — copy-paste source for LinkedIn |
| `report.docx` | Posting instructions, image ranking, what changed, items needing verification, AI-image disclosure |
| `review_report.docx` | Reviewer skill output — typo / brand / hype density findings |
| `images_used/` | Processed image candidates (ranked top 10 or all if <10) |

Conversion command (Codex runs internally):

```bash
python3 _helpers/build_docx.py <input.md> <output.docx> --images images_used/*
```

The helper embeds images inline in the .docx and color-codes severity
labels (CRITICAL/WARNING/SUGGESTION) for the report.

**No `.md` output** in v0.3.0. Markdown is the working format; users see
only Word.

---

## Phase 9 — Memory and feedback

After delivering output, the skill waits for user feedback in chat.

Feedback handling follows the three-path rule in `_rules/memory_policy.md`:

1. **Decline** — discard, no record
2. **This run only** — apply now, log in `report.docx`, no memory write
3. **Save as permanent rule** — apply now + translate informal feedback to formal rule + append to `user_memory.md` + log in `memory_change_log.md`

Codex always **asks** which path before writing to memory. Never silently
saves rules.

---

## Constraints

- **English only.** No multi-language support in v0.3.0 (LinkedIn for CDHAI is English audience).
- **No direct posting.** The skill produces drafts. Human review required before publishing. Compliance: Gordon's directive, May 10 2026 meeting.
- **Images optional but strongly recommended.** Text-only posts are allowed but flagged in report as "consider adding visual" — LinkedIn engagement is 2-3x higher with images.
- **API keys are user-provided.** Skill never ships with keys. Missing keys → fallback to user-provided / extracted images only.

---

## File map

```
cdhai-social-media-officer-linkedin.skill/
├── SKILL.md                          ← you are here
├── VERSION                           ← 0.3.0
├── README.md
├── install.sh
├── skill.config.json
├── _rules/
│   ├── content_types.md              ← NEW in v0.3
│   ├── linkedin_style.md             ← NEW in v0.3 (replaces banned_words)
│   ├── asset_policy.md               ← NEW in v0.3
│   ├── inspiration_corpus.md         ← updated with tone analysis
│   ├── brand_rules.md                ← updated hashtag policy
│   ├── memory_policy.md              ← updated 3-path clarity
│   ├── core_rules.md
│   └── permission_policy.md
├── _template/
│   ├── linkedin_post_template.md
│   └── report_template.md            ← updated with "Ready to publish"
├── _memory_template/
│   ├── user_memory.md
│   └── memory_change_log.md
├── _helpers/
│   ├── build_docx.py                 ← NEW in v0.2.1 / 0.3
│   ├── unsplash_search.py
│   └── dalle_generate.py
├── examples/
│   └── sample-cheetah-content.md
└── docs/
    └── usage.md
```

---

## What changed in v0.3.0 vs v0.2

- Output is `.docx` not `.md` (Gordon's directive: "we love to see pages")
- Content types: 5 → 9 (added awards_grants, people_announcement, partnership_announcement, general)
- Length: automatic per content_type, not user-chosen short vs standard
- Hashtags: 3-5 default 4 (was hard ≤3 inherited from Carey website policy; LinkedIn norm differs)
- Banned words list dropped — replaced with density-based judgment in reviewer skill
- Image picking: top 10 ranked (was pre-decided 1-3)
- Inspiration corpus formalized with tone analysis (warm_professional dominant)
- Memory three-path documented clearly in `memory_policy.md`
- Asset fallback flow when no images uploaded
- `report.docx` includes "Ready to publish" instructions
