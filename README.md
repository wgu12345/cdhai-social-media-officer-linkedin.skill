# CDHAI Social Media Officer — LinkedIn (v0.4.2)

A Codex skill that drafts LinkedIn posts for the **Center for Digital
Health and Artificial Intelligence** at Johns Hopkins Carey Business
School.

## What v0.4.2 buys you

- **Zero API keys required.** Codex is itself GPT — no reason to also call OpenAI's API. v0.4.2 uses Codex's native multimodal capabilities for all vision (Tier 1 image description, Tier 2 face comparison), all paper analysis, and all reviewer judgment.
- **Reviewer runs as a Codex sub-agent**, with fresh context. Independent eyes, not "same model reviewing its own draft."
- **Image processing is batched** (5 images per batch, manifest written to disk between batches) to keep context tight and avoid attention degradation.
- **Image diversity constraints** prevent over-representation. If Gordon is in 8 of 13 photos, he still occupies max 2 of the final 5 slots. Other Key Points get other visuals.
- **Web-sourced images** carry a mandatory legal warning at the top of `before_you_post.docx`, with per-image source URL and a manual rights-verification checkbox.

## What v0.4 brought (carried forward)

- Word content template required (Purpose, Post Type, Date, Key Points, Background, Notes)
- 9 reviewer checks including `key_points_coverage`, `generic_density`, `image_match`
- Tier 1 / Tier 2 / Tier 3 image matching
- Research paper analysis (Level 3)
- Date fact-checking
- Codex built-in `$imagegen` for AI image generation (no API key)
- Inline embedded images in `linkedin_post.docx`
- Single merged `before_you_post.docx` report

Companion skill: [cdhai-content-reviewer.skill](https://github.com/wgu12345/cdhai-content-reviewer.skill).

---

## Why this isn't just ChatGPT

| Same input → different outputs | ChatGPT | CDHAI LinkedIn Skill |
|---|---|---|
| Multiple source files disagree | Picks one or fabricates a synthesis | Detects the conflict, refuses to commit, flags for human |
| Source contains unverified material | Often quotes it anyway | Refuses to quote without source-of-truth |
| Brand consistency (CHITA not CHEETAH, JHU Carey full name on first mention) | Up to whoever prompts | Hard-coded in `_rules/brand_rules.md`, applied automatically |
| 13 photos, 5 are Gordon — which fit which Key Point? | Doesn't handle images that way | Vision describes each, web-searches for named people, **diversity-constrains so no one person dominates** |
| Audit trail of decisions | None — output is "what it said" | Every choice traceable in `before_you_post.docx` |
| Hashtag rules (LinkedIn 2026 norms) | Generic, often wrong | Embedded in `_rules/brand_rules.md` |
| Team consistency | Different output per prompt | Same skill, same SKILL.md, same outputs across the team |
| Skill memory | None persistent | Three-path: this-run / save-permanently / decline |
| Web image legal exposure | Posts whatever | Hard legal warning + reviewer CRITICAL flag until rights verified |

The skill is the team's **shared brain**. ChatGPT is one person's prompting session.

---

## What it does, in one breath

```
User's folder:
├── content.docx                ← filled-in template (Purpose, Post Type, Date, Key Points)
├── (PDFs)                       ← papers, agendas, slides
└── (images)                     ← visual candidates
            ↓
       cdhai-social-media-officer-linkedin
       (auto-invokes cdhai-content-reviewer as sub-agent at the end)
            ↓
Same folder gets:
├── linkedin_post.docx          ← post with inline embedded images
└── before_you_post.docx        ← merged verification report
                                  (with diversity check + legal warnings if applicable)
```

---

## Installation

### One-time setup

```bash
git clone https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill ~/cdhai-skills/cdhai-social-media-officer-linkedin.skill
git clone https://github.com/wgu12345/cdhai-content-reviewer.skill ~/cdhai-skills/cdhai-content-reviewer.skill
bash ~/cdhai-skills/cdhai-social-media-officer-linkedin.skill/install.sh
bash ~/cdhai-skills/cdhai-content-reviewer.skill/install.sh
```

**No API keys to add.** Codex handles all AI work. The optional
`serpapi_key` field in `~/.cdhai-linkedin-skill/config.json` gives slightly
cleaner web search for Tier 2 face identification, but DuckDuckGo fallback
works fine without it.

### Via Codex App

1. Open Codex App → Plugins → Install from URL.
2. Paste `https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill`.
3. Repeat for `https://github.com/wgu12345/cdhai-content-reviewer.skill`.
4. That's it. No keys to configure.

---

## Using the skill

### Step 1 — Prepare your folder

Copy `_template/content_template.docx` from the installed skill into a
new folder. Fill in:

- **Purpose** — one sentence
- **Post Type** — pick one of nine
- **Date** — event / publication / announcement date
- **Key Points** — every one will appear in the post (the skill enforces this)
- **Background / Source Materials** — free-form context (optional)
- **Notes for the writer** — tone preferences (optional)

Save as `content.docx`. Drop into the working folder.

### Step 2 — Add supporting materials

- The **paper PDF** if Post Type is `research_published`
- The **agenda PDF** if Post Type is `event_recap` or `upcoming_event`
- **Photos** (any number, ideally 5+)
- Anything else relevant (Word, PDF, txt)

### Step 3 — Run in Codex

```
Use the cdhai-social-media-officer-linkedin skill on this folder.
```

The skill:
1. Reads your content template
2. Reads all PDFs and images
3. **Describes every image directly** (Codex multimodal native, batched 5 at a time)
4. **Web-searches for official photos of named people** (helper does download, Codex does face comparison)
5. **Matches every Key Point to a candidate image**
6. **Applies diversity constraints** — no single subject or scene type dominates
7. **Asks you for missing-image fallbacks** (your own / `$imagegen` / web search / skip)
8. Analyzes any research paper PDF (Codex reads the pypdf-extracted text)
9. Fact-checks dates
10. Generates the draft
11. **Spawns a sub-agent** to run the reviewer (independent fresh-eyes pass)
12. Loops on critical issues (max 3 revisions)
13. Saves `linkedin_post.docx` + `before_you_post.docx` to your folder

### Step 4 — Read, edit, post

1. Open `before_you_post.docx`. Address the legal-warning banner (if any web images), then the Must verify section.
2. Open `linkedin_post.docx`. The post text with embedded image previews.
3. Copy text to LinkedIn. Drag images from Word to LinkedIn's upload, or pull from your original folder.
4. Publish.

---

## The image-text matching subsystem

**Tier 1 — Codex describes every image natively.** Batched 5 at a time, output written to a manifest file on disk between batches.

**Tier 2 — Web search + face comparison.** Helper does deterministic web search ("Ritu Agarwal JHU Carey" → Carey faculty page → headshot download). Codex compares the reference photo with each candidate image natively.

**Diversity check — NEW v0.4.2.** Caps any single subject at 2/5 picks, any single scene type at 2/5. Rebalances when violated.

**Tier 3 — Fallback when no match.** Asks the user:
- (a) Provide your own image [RECOMMENDED]
- (b) Generate with Codex's built-in `$imagegen` (uses your ChatGPT plan, not API credits)
- (c) Search the web for an image — ⚠ **every web-sourced image requires manual usage-rights verification before posting**
- (d) Skip this Key Point's visual anchor

Minimum 5 images per post.

---

## The nine reviewer checks

Detailed specs in `cdhai-content-reviewer.skill/_rules/`.

| # | Name | Purpose |
|---|---|---|
| 1 | typos_and_grammar | Copy-edit + proper-noun cross-reference |
| 2 | brand_consistency | Naming, capitalization, branded hashtag compliance |
| 3 | factual_flags | Uncited claims, ambiguous attributions, dates |
| 4 | hype_density | Sliding-window scan for AI-cliché jargon |
| 5 | hashtag_check | Count, placement, casing, composition |
| 6 | hook_quality | Forbidden openers; required hook patterns |
| 7 | key_points_coverage | Every Key Point must appear (CRITICAL if missed) |
| 8 | generic_density | Every body paragraph must have a specific anchor |
| 9 | image_match | Manifest sanity; web-image rights verification flag |

The reviewer runs as a Codex **sub-agent** with fresh context for
independence.

---

## Memory: local vs global

- **Local memory** (your personal rules): `~/.cdhai-linkedin-skill/memory/user_memory.md`. Personal, never synced.
- **Global rules** (the skill's behavior): `SKILL.md` + `_rules/*.md` in this repo. To change globally, push to GitHub.

Three-path memory:
1. **Decline** — discard.
2. **This run only** — apply, log in report, no save.
3. **Save as permanent rule** — apply + translate informal feedback to formal rule + append to `user_memory.md`.

The skill **always asks** which path. Never silently saves rules.

---

## Constraints

- **English only.** Multilingual on v0.6.
- **Drafts only — no auto-posting.** Human review required. Compliance directive from Gordon.
- **Word required as primary input.**
- **No API keys required.** Codex handles all AI work.
- **Web access required.** Tier 2 face identification + Tier 3 (c) web image search.
- **Web-sourced images require manual usage-rights verification.** Enforced by warning banner + reviewer CRITICAL flag.

---

## File map

```
cdhai-social-media-officer-linkedin.skill/
├── SKILL.md                          ← entry point
├── VERSION                           ← 0.4.2
├── README.md
├── install.sh
├── skill.config.json
├── _rules/
│   ├── content_types.md
│   ├── linkedin_style.md
│   ├── asset_policy.md
│   ├── image_matching.md
│   ├── image_diversity.md            ← NEW v0.4.2
│   ├── paper_analysis.md
│   ├── date_factcheck.md
│   ├── inspiration_corpus.md
│   ├── brand_rules.md
│   ├── memory_policy.md
│   ├── core_rules.md
│   └── permission_policy.md
├── _template/
│   └── content_template.docx
├── _helpers/                         ← DETERMINISTIC ONLY in v0.4.2
│   ├── build_docx.py                 ← python-docx (post + report)
│   ├── face_compare.py               ← --identify only (web + download)
│   ├── pdf_paper_extract.py          ← pypdf text only
│   └── web_image_search.py           ← Bing/DDG scraping
├── _memory_template/
│   ├── user_memory.md
│   └── memory_change_log.md
├── docs/
│   └── team-guide.md
└── examples/
    └── filled-template-example/
```

---

## Maintainer

Wenying Gu (github.com/wgu12345) — CDHAI / Carey Business School

License: internal CDHAI use.
