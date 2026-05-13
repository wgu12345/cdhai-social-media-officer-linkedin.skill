# cdhai-social-media-officer-linkedin

A Codex / Claude Code skill that drafts LinkedIn posts for the **Center for
Digital Health and Artificial Intelligence (CDHAI)** at Johns Hopkins Carey
Business School.

Built so program coordinators, postdocs, and MarComm staff can produce
publish-ready drafts without writing prompts. Drops into Codex App or CLI;
runs against a folder; outputs Word documents.

**Companion**: [`cdhai-content-reviewer.skill`](https://github.com/wgu12345/cdhai-content-reviewer.skill)
runs after this skill to flag typos, brand inconsistencies, hype density,
and items needing verification. The two are designed to chain.

---

## What this skill is, and isn't

**Is**: a LinkedIn-specific draft generator for CDHAI / Carey content. Takes a folder, returns a Word doc you can copy-paste into LinkedIn after human review.

**Isn't**:
- A direct poster — outputs drafts only, never publishes. CDHAI policy (Gordon Gao, May 10, 2026) requires human review before any post goes live.
- A general blog generator — for web pages, use [Jiayi's `carey-blog-page-generator.skill`](https://github.com/coreyjhu-ops/carey-blog-page-generator.skill). Different output format, different conventions.
- A multi-platform tool — LinkedIn only in v0.3. Twitter / Instagram / JHU website are separate skills (not yet built).
- A multilingual tool — English only in v0.3.

---

## Quick start

```bash
# Put your post folder somewhere accessible. Example structure:
~/Desktop/cheetah-recap/
├── content.docx          # what the post is about
├── images/               # event photos (strongly recommended)
│   ├── keynote_01.jpg
│   └── audience_02.jpg
└── style_reference.pdf   # optional visual reference
```

In Codex App (or CLI) with this folder as the project:

> *"Use the cdhai-social-media-officer-linkedin skill on this folder."*

Codex produces, in the same folder:

- `linkedin_post.docx` — the draft, ready to copy-paste
- `report.docx` — posting instructions, image ranking, items needing verification
- `review_report.docx` — typo and brand check from the reviewer skill
- `images_used/` — top 10 image candidates ranked by relevance

---

## Design decisions — what, why, what we referenced, where the boundaries are

The 13 decisions below shaped how the skill behaves. Skills are packaged,
so the README has to do the explaining the code can't.

### 1. Nine content types

**What**: the skill detects which of 9 categories a post falls into, then sets the right default length and tone.

| Type | Tone default | Length target |
|---|---|---|
| `event_recap` | warm_professional | ~1,300 chars |
| `upcoming_event` | warm_professional | ~700 chars |
| `faculty_presentation` | warm_professional | ~1,000 chars |
| `research_published` | warm_professional | ~1,200 chars |
| `thought_leadership` | warm_professional | ~1,400 chars |
| `awards_grants` | warm_playful | ~600 chars |
| `people_announcement` | warm_playful | ~750 chars |
| `partnership_announcement` | warm_professional | ~800 chars |
| `general` | warm_professional | ~900 chars |

**Why 9**: v0.2 had 5 types (event_recap, upcoming_event, faculty_presentation, research_published, thought_leadership). Looking at CDHAI's actual LinkedIn presence and peer centers, 4 patterns were missing — grant wins (CDHAI just had one), people announcements (faculty hires like Andrew Burton-Jones, student graduations like Harang Ju's), partnership announcements (Stanford HAI does these for corporate affiliates), and a catch-all for everything else.

**What we referenced**: CDHAI mentions on Carey's LinkedIn page; Stanford HAI; MIT Jameel Clinic; Wharton AI Lab; HBS; Yale Digital Ethics; JHU CIL. ~50 recent posts across these accounts.

**Boundaries**: if Codex's top guess is below 70% confidence OR the top two types are within 10% of each other, the skill **asks the user** rather than guessing. `general` is the catch-all — partnership posts can fall here if they're light on partnership specifics.

### 2. Three tones, warm_professional default

**What**: each post is generated in one of three tones — `warm_professional` (default), `warm_playful` (celebrations), or `formal_serious` (rare).

**Why three not one**: a grant win calls for celebration; a privacy white paper calls for restraint; a research recap calls for warm professional. One tone wouldn't fit them all. Three covers what peer institutions actually publish.

**What we referenced**: tone distribution analysis of ~50 peer LinkedIn posts (Stanford HAI, MIT Jameel, etc.):
- `warm_professional` ≈ 70% of posts (research shares, event recaps, faculty intros, opinion pieces)
- `warm_playful` ≈ 25% (grant wins, anniversaries, graduations, holidays; more emoji)
- `formal_serious` ≈ 5% (privacy/ethics releases, large foundation grants with external brand co-mentions)

**Boundaries**: tone defaults are set per content_type (see table above). User can override in chat; override applies to that run unless saved as a permanent rule via the three-path memory (see #9).

### 3. Detection confidence threshold: 70%

**What**: when Codex detects content_type, if the top candidate is below 70% confidence or the top two are within 10% of each other, the skill stops and asks the user which type fits.

**Why 70%**: empirically the point where Codex's guess is reliable. Below that, asking is cheap; guessing wrong wastes the user's time on a re-run.

**Boundaries**: this is a "stop and ask" mechanism, not a confidence display. Users don't see the percentage; they only see the question when it triggers.

### 4. Single output, length set automatically

**What**: one LinkedIn post per run, length determined by content_type, not user choice.

**Why not two versions (standard + short) like v0.2**: producing both doubled review burden. In practice MarComm picks standard 95% of the time. If a draft is too long, that's a chat-revision moment, not a reason to pre-produce alternatives.

**What we referenced**: LinkedIn 2026 algorithm research — longer posts work IF dwell time is strong. Length should match content richness; padding hurts engagement. Targets above are based on average lengths in Stanford HAI / MIT Jameel posts of each type.

**Boundaries**: targets are guidance, not hard caps. Codex aims for the target naturally based on input; it doesn't pad to hit it. If user says "too long" in chat, it's a one-time edit or a save-as-rule memory event (see #9).

### 5. Hashtags: 3-5, default 4

**What**: each post ends with 3-5 hashtags; default is 4. Composition: 1 broad + 1-2 niche + 1 branded.

**Why not 3 like Carey's website policy**: Carey's 3-hashtag rule was written for `carey.jhu.edu` blog posts (the platform Jiayi's skill targets). LinkedIn 2026 norms differ — algorithm research shows 1-3 hashtags average 14.7 likes per post; 3-5 is LinkedIn's official guidance; >5 triggers spam filter. CDHAI on LinkedIn should follow LinkedIn norms.

**What we referenced**: LinkedIn's official 2026 hashtag guidance; van der Blom 2026 algorithm research (1.3M post analysis); Sprout Social and ConnectSafely 2026 hashtag guides.

**Boundaries**: hard upper bound is 5 (above this, LinkedIn's spam filter kicks in). Hashtags go at the end of post, never in the hook. Casing is PascalCase or camelCase (`#DigitalHealth`, `#AIinMedicine`), never all-lowercase. Mix: include at least one branded/event tag (`#CDHAI`, `#JHUCarey`, `#CHITA2026`, `#SitHigh`) when relevant.

### 6. No banned-words list — density-based judgment instead

**What**: there is no hard banlist. Words like `robust`, `cutting-edge`, `transformative` are allowed; the companion reviewer skill flags stretches where multiple hype words pile up.

**Why density not banlist**: v0.2 banned 14 words including `robust` (a legitimate statistical term) and `cutting-edge` (which Stanford HAI and MIT Jameel use in real posts). Banning specific words produces stilted prose that doesn't sound like CDHAI. The actual problem isn't any single word — it's when several hype words appear close together, making prose feel like generic PR.

**What we referenced**: real LinkedIn posts from Stanford HAI ("cutting-edge"), MIT Jameel ("transforming our understanding", "revolutionizing"), and CDHAI on Carey ("groundbreaking grant"). Peer institutions use these words; banning them would push our voice away from theirs.

**Boundaries**: the reviewer skill defines a sliding 200-character window. Words are tiered:
- **Tier 1** (pure jargon, weight 1.5): leverage, synergize, best-in-class, world-class, game-changing, disrupt
- **Tier 2** (overused but sometimes apt, weight 1.0): cutting-edge, revolutionary, transformative, seamless, unlock, utilize, paradigm, passionate, "excited to announce", "delighted to share"
- **Tier 3** (legitimate, weight 0): robust, novel, significant

If any 200-char window's weighted sum ≥ 3.0, the reviewer flags it. **The reviewer never auto-edits.** It only flags. Human decides.

### 7. Inspiration corpus from peer institutions

**What**: `_rules/inspiration_corpus.md` contains voice analysis of 6 peer academic AI centers. Codex reads it before writing.

**Why peer corpus instead of hard-coded rules**: voice can't be captured in a rulebook. Showing Codex what good CDHAI-style writing looks like is more effective than telling it "be warm but professional." The corpus is the primary mechanism for style; bullets in `linkedin_style.md` are reminders.

**What we referenced**: Stanford HAI (linkedin.com/company/stanfordhai); MIT Jameel Clinic - AI & Health (linkedin.com/company/aihealthmit); Wharton AI Lab; HBS; Yale Digital Ethics; JHU Carey (CDHAI mentions). Each profile analyzed for tone distribution, emoji frequency, hashtag patterns, hook style, sentence rhythm.

**Boundaries**: the corpus is descriptive (text summaries of voice), not active-fetched. Future enhancement (v0.4+): periodic refresh from live URLs. For now, manual quarterly review by the maintainer.

### 8. Ask-when-missing as principle, not checklist

**What**: before finalizing a draft, Codex scans for claims that a thoughtful reader would have to Google to verify. If the source-of-truth isn't in the input materials, it asks the user.

**Why principle not list**: a rule list can't anticipate every case. The classic example: name transliteration. "Aggarwal" or "Agarwal" — both are valid spellings of the same surname; a list-based rule wouldn't catch the ambiguity, but the verify-by-Googling test does ("could a reader confirm which spelling is correct?").

**Categories that commonly trigger the test** (not exhaustive):
- Name spelling variants (especially South Asian and East Asian names)
- Missing name components (first only, last only, title missing)
- Date ambiguity ("yesterday" without anchor)
- Location specificity ("Hopkins" — which campus?)
- Uncited numeric claims
- Attribution ambiguity ("the team said X" — which team?)
- Acronyms not expanded on first use

**Boundaries**: Codex asks at most once per ambiguous item per run. If the user is clearly unavailable (long delay), Codex notes the uncertainty in `report.docx` under "Items flagged for human verification" and proceeds with the best-effort draft.

### 9. Three-path memory

**What**: when user gives feedback in chat ("the hook is too long", "always include a CTA"), the skill asks how to handle it. Three options:

- **Decline** — discard, no record, no apply
- **This run only** — apply now, log in `report.docx`, don't write to `user_memory.md`
- **Save as permanent rule** — apply now + translate informal feedback to formal rule + append to `~/.cdhai-linkedin-skill/memory/user_memory.md` + log in `memory_change_log.md`

**Why three not two**: Jiayi's skill has two (save / decline). The middle path is needed for one-off corrections ("for this CHEETAH recap, mention Andrew Burton-Jones") that shouldn't carry forward as a rule but should be auditable in the report.

**The translation step** (Path 3): user feedback is informal ("don't make it sound corporate"); the rule that goes into memory must be formal and unambiguous so future Codex sessions apply it correctly ("avoid hype words from the Tier 1/2 list when 3+ would appear in a 200-char window; prefer concrete and specific language"). The translation always happens before the user confirms — they see the formal version and approve it.

**Boundaries**: rules that conflict with brand rules (e.g., "use 7 hashtags" exceeding LinkedIn's hard cap of 5) trigger a clarification dialog. Memory never silently overrides brand or compliance rules.

### 10. Severity levels (reviewer skill)

**What**: the companion reviewer skill produces findings in three severity buckets:

- **CRITICAL** — must address before posting (misspelled proper nouns, factual errors in central claims, brand-rule violations on names like `MSAI` vs `MS-AI`)
- **WARNING** — verify before posting (uncited numbers, unanchored dates, ambiguous attribution, hype density flag)
- **SUGGESTION** — optional polish (acronym expansion, hook clichés like "excited to announce", hashtag casing)

**Why three levels not flat**: a misspelled faculty name and an optional comma fix shouldn't get the same visual weight. Severity guides the reviewer's eye to what matters.

**Boundaries**: severity is the reviewer's judgment, not a hard classification. Edge cases (is "Dr. Yang" with no first name a critical or warning?) lean conservative — when in doubt, escalate one level.

### 11. Asset acquisition — four sources, fallback flow when none

**What**: images come from up to four sources, tried in this order:
1. User-provided in `images/` folder
2. Auto-extracted from PDF/DOCX content files
3. Unsplash CC-licensed search (requires API key)
4. DALL-E generation (requires OpenAI API key; **flagged as AI in `report.docx`**)

**When all four return zero images**, the skill stops and asks:
> "I don't see any images. Pick one: (a) search Unsplash, (b) generate via DALL-E, (c) text-only."

It does NOT silently proceed with a text-only post. Users decide.

**Why this flow**: LinkedIn engagement is 2-3x higher with images. Silently producing text-only would underdeliver. But forcing image upload would be too rigid — sometimes the user actually wants text-only.

**Boundaries**: API keys for Unsplash and DALL-E go in `~/.cdhai-linkedin-skill/config.json` (you fill in your own). Missing keys → that source is skipped; the skill proceeds with whatever's available. AI-generated images are always flagged in `report.docx` under "AI-generated images used" — per JHU social-media guidelines on AI content disclosure.

### 12. Slides handling and style reference

**Slides (`.pptx`, `.key`)**: native parsing isn't supported in v0.3. Workaround: export your deck to PDF, drop it in the folder. The skill's PDF extraction handles both text and embedded images, so the workaround is lossless for most cases. Native `.pptx` support is on the v0.4+ roadmap.

**Style reference (`style_reference.{txt,html,pdf}`)**: optional input that helps the skill match a preferred visual or tonal direction.

- For LinkedIn alone, style reference matters less — LinkedIn strips visual styling on paste.
- **As CDHAI extends to web pages and visual content**, style reference becomes essential. Recommended even now to build the muscle for when it matters.

**URL handling edge case**: if you provide a URL as the style reference and Carey's site blocks bots (returns 403), the skill **instructs you to download the page as HTML or PDF** rather than failing silently. Provide the downloaded file in the folder.

### 13. Image picking — top 10 ranked, user decides

**What changed from v0.2**: v0.2 pre-decided 3 images. v0.3 ranks the top 10 and lets the user pick the final 1-3 for LinkedIn.

**Why 10 not 3**: pre-deciding 3 made wrong choices ~30% of the time in v0.2 testing. Presenting 10 ranked with rationale lets the human apply their judgment — they know context the AI doesn't (e.g., "we're not allowed to show that speaker's face yet"). LinkedIn allows multiple images per post but 1-3 is the typical pick.

**Ranking criteria** (applied in order):
1. Semantic match to post content
2. Source priority: user-provided > PDF-extracted > Unsplash > DALL-E
3. Resolution (≥1200px wide preferred)
4. Recency

**Output**: `report.docx` includes a ranked table with a one-line reason per image ("image_05: matches keynote speaker mentioned in paragraph 2"). If fewer than 10 images exist, all are shown ranked.

**Boundaries**: the skill never auto-selects which images go to LinkedIn. The human picks from the ranked list when uploading to LinkedIn.

### Bonus: Posting instructions in report.docx

`report.docx` now ends with a "Ready to publish" section so non-technical reviewers don't have to think about where to click:

> 1. Open `linkedin_post.docx`
> 2. Select all text → copy → paste into LinkedIn "Create a post"
> 3. Upload these images in the order ranked above (pick 1-3)
> 4. Hashtags are already at the end of the text — no separate action
> 5. Best posting time: Tue-Thu 9-11 AM ET (CDHAI audience peak)

The intent is everything-needed-in-one-place so MarComm can publish without back-and-forth.

---

## Folder convention

```
your_post_folder/
├── content.{md,txt,docx,pdf}        # main content (required)
├── images/                          # photos (strongly recommended)
│   ├── image_01.jpg
│   └── ...
├── style_reference.{txt,html,pdf}   # optional, see #12
└── (any other supporting docs)
```

After running the skill, the same folder also contains:

```
your_post_folder/
├── (your inputs above)
├── linkedin_post.docx               ← the draft
├── report.docx                      ← posting instructions, ranking, audit
├── review_report.docx               ← reviewer skill findings
└── images_used/                     ← top 10 ranked candidates
```

---

## Install

Either via Codex App (preferred for non-technical users):

> In Codex App: Plugins → "Install from URL" → paste:
> `https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill`

Or via CLI:

```bash
git clone https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill.git
cd cdhai-social-media-officer-linkedin.skill
bash install.sh
```

`install.sh` creates `~/.cdhai-linkedin-skill/` (memory + config + cache),
installs Python dependencies (`python-docx`, `Pillow`, `pypdf`, `requests`,
`beautifulsoup4`), and copies skill files into the right Codex location.

A team-facing onboarding guide with screenshots lives in `docs/team-guide.md`.

---

## Configure

Edit `~/.cdhai-linkedin-skill/config.json`:

```json
{
  "unsplash_access_key": "",
  "openai_api_key": "",
  "github_version_check": true,
  "language": "en"
}
```

Keys are stored locally, never committed. If missing, the skill falls back to user-provided and PDF-extracted images only (still works — just no Unsplash or DALL-E option).

---

## How this differs from Jiayi's `carey-blog-page-generator.skill`

| | Jiayi's blog skill | This skill |
|---|---|---|
| Output | HTML web page | LinkedIn post (.docx) |
| Skill count | 1 | 2 (writer + reviewer, chain together) |
| Content types | Generic blog | 9 LinkedIn-specific, auto-detect |
| Voice source | Hardcoded Carey HTML template | Peer institution corpus |
| Voice variation | Single tone | 3 tones (default warm_professional) |
| Missing info | Notes in report | Asks user mid-flow (verify-by-Googling) |
| Memory | 2 paths (save / decline) | 3 paths (decline / this run / save as rule) |
| Image sources | User-provided only | User + extract + Unsplash + DALL-E + fallback |
| Hype words | Not addressed | Density check (no banlist) |

Both are owned by individual contributors in the CDHAI ecosystem. They're complements, not competitors — Jiayi's covers web pages, this covers LinkedIn. Future skills (Twitter, Instagram, JHU website) will follow the same pattern.

---

## Compliance and constraints

- **Drafts only.** This skill never publishes. Human review is required before any LinkedIn post goes live. CDHAI policy, Gordon Gao directive, May 10 2026.
- **AI-generated images are flagged.** Any image produced by DALL-E appears in `report.docx` under "AI-generated images used" — per JHU social-media guidelines on AI content disclosure.
- **No quoting living individuals** without their material being source-of-truth (a published interview, public talk). When in doubt, the skill flags for verification rather than guessing.
- **No partner/sponsor mentions without coordination** — if a corporate partner or sponsor is referenced in your input, the skill flags this in `report.docx` so you can confirm with CDHAI partnership office before posting.
- **English only** in v0.3.
- **LinkedIn only** in v0.3. Other platforms get their own skills.

---

## Versioning

| Version | Key changes |
|---|---|
| v0.1.0 | Initial skill, basic LinkedIn drafts in markdown |
| v0.2.0 | 5 content types, 3 tones, inspiration corpus, ask-when-missing, 3-path memory, dual standard+short output |
| v0.3.0 | DOCX output replacing MD; 9 content types (added awards, people, partnership, general); single output with auto length; hashtags 3-5 default 4 (was hard 3); banned-words list dropped in favor of density-based reviewer check; top-10 image ranking with user pick; asset fallback flow when no images present; explicit "Ready to publish" section in report; tone analysis from peer corpus formalized |

Codex checks `VERSION` against GitHub on every invocation and warns if local is behind.

---

## Roadmap

- **v0.3.x** — bug fixes from real-world MarComm use, additional content type detection signals
- **v0.4** — native `.pptx` parsing; live URL refresh for inspiration corpus
- **v0.5** — additional platform skills (Twitter, Instagram, JHU website)
- **Beyond** — multilingual support; direct post integration (requires CDHAI policy change)

---

## Owner

Wenying Gu ([@wgu12345](https://github.com/wgu12345))
Built for the CDHAI team at Johns Hopkins Carey Business School.

Owner accepts PRs from CDHAI collaborators directly; others should open an
issue first to discuss direction. Bugs, feature requests, and design
critiques all welcome in the issue tracker.
