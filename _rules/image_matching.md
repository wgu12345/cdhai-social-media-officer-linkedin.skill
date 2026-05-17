# Image Matching Policy — Tier 1 / 2 / 3 (v0.4.2)

Every Key Point in the user's content template must have at least one
matched image. The skill ranks images using a three-tier system. This
rule defines what each tier does, how scores are computed, and what to
do when matches fail.

**v0.4.2 architecture note**: All vision tasks are performed by Codex
directly (multimodal native), not by external API calls. Helpers handle
only deterministic work (web search, image download, HTML scraping).
Diversity constraints from `image_diversity.md` run after per-Key-Point
matching but before Tier 3 fallback.

---

## Tier 1 — Vision description + semantic match (Codex native)

For every image in the user's folder, Codex performs this directly. No
helper script is called.

### Step 1a — Describe every image (batched)

To manage context window, Codex processes images in batches of 5:

```
For batch i = 1 to ceil(N/5):
  Look at the 5 images in this batch directly.
  Produce 5 JSON entries, one per image, matching the schema in SKILL.md Phase 4.
  Append to ~/.cdhai-linkedin-skill/cache/image_manifest_<run_id>.jsonl
  Summarize the batch in one line to keep context tight.
  Discard the per-image details from active context; the file on disk is the source of truth.
```

The JSON schema (from SKILL.md Phase 4):

```json
{
  "path": "/absolute/path/to/image.jpg",
  "scene_summary": "1-2 sentence factual description",
  "people_count_approx": <integer>,
  "named_subjects_visible": ["<only if high-confidence>"],
  "visible_text": ["banner text", "signage"],
  "setting": "indoor_podium | indoor_panel | indoor_classroom | indoor_lab | indoor_reception | indoor_office | outdoor_campus | outdoor_other | screenshot | document | unclear",
  "estimated_quality": "high | medium | low",
  "tags": ["short", "descriptive", "tags"]
}
```

### Step 1b — Match against each Key Point

For each Key Point, Codex:

1. Constructs a target description (what would the ideal image look like?).
2. Reads the manifest from disk.
3. Scores each image's description against the target on:
   - **Topic match**: scene type fits the Key Point's substance?
   - **Setting match**: institutional signage visible (CDHAI / JHU)?
   - **Object match**: relevant objects (whiteboard, slides, podium, etc.)?
4. Combined score 0-1. **≥0.7 = strong match**. **0.4-0.7 = partial**. **<0.4 = unrelated**.

If a strong match is found in Tier 1 alone, Tier 2 is not needed for
that Key Point.

---

## Tier 2 — Specific person identification (Codex native vision + web helper)

Triggered when a Key Point references a named person AND no strong Tier 1
match was found OR multiple candidates need disambiguation.

### Step 2a — Web search for an official photo (helper)

```bash
python3 _helpers/face_compare.py --identify "<Full Name>"
```

The helper does **only** the deterministic work:
- Searches Carey / JHU / CDHAI / Hopkins pages (priority order)
- Downloads the most-likely headshot
- Caches it for 90 days at `~/.cdhai-linkedin-skill/cache/reference_<hash>.jpg`
- Returns JSON with `cached_image_path` and `source_url`

Query priority (helper tries in order):

1. `"<Full Name>" Johns Hopkins Carey faculty`
2. `"<Full Name>" CDHAI Johns Hopkins`
3. `"<Full Name>" Hopkins medical AI`
4. `"<Full Name>" JHU faculty bio`
5. `"<Full Name>" Carey Business School`

### Step 2b — Codex compares the reference photo with each candidate

**Codex itself performs the face comparison by looking at both images.**
No API call. For each candidate image:

```
Look at the reference photo and the candidate image. Determine if the
person in the reference is also present in the candidate. Output JSON:

{
  "candidate_path": "...",
  "reference_path": "...",
  "same_person_confidence": <0.0 to 1.0>,
  "justification": "one short sentence",
  "notes": "optional caveats (angle, lighting, partial occlusion)"
}

Scoring guide:
- 0.90-1.00: Clear face match. Same person beyond reasonable doubt.
- 0.70-0.89: Likely same person. Some uncertainty (angle / lighting).
- 0.40-0.69: Plausible but not confident.
- 0.10-0.39: Probably different people.
- 0.00-0.09: Clearly different people.

Be strict. A false positive (saying same when not) is worse than a false negative.
```

### Step 2c — Decide

For each Key Point with a named person:

- **≥0.8** → high-confidence match → assign + note in report
- **0.5-0.8** → tentative + flag "verify before posting"
- **<0.5** → fall through to Tier 3

### Step 2d — Coverage limitations

If web search returns nothing usable for the named person:

> Tier 2 could not find a reference photo for <name>. Falling back to
> Tier 1 description match. Verify image choice manually.

Continue with Tier 1; do not block the run.

---

## Diversity check (between Tier 2 and Tier 3) — v0.4.2

After per-Key-Point matching, run the diversity algorithm from
`image_diversity.md`:

1. Tally subjects across all picks.
2. Tally scene types.
3. If any subject appears in more than 2 picks (out of 5), or any scene
   type appears in more than 2 picks → rebalance.
4. Rebalancing releases the lowest-confidence over-represented picks
   and re-matches their Key Points.
5. Re-matched Key Points that find no alternative → trigger Tier 3.

This step protects against the common case where one person (e.g.,
Gordon) is photographed many times but should not occupy 3 of 5 final
slots.

---

## Tier 3 — Fallback when no match exists

If a Key Point ends with no match (Tier 1 < 0.4 AND Tier 2 < 0.5, OR
released by the diversity step), the skill consults the user:

```
The Key Point "<exact text>" has no matching image in your folder.

Pick one:
(a) Provide your own image — I'll wait, then re-run.  [RECOMMENDED]
(b) Generate with Codex's built-in $imagegen skill.
    (AI-generated; flagged in report.)
    Suggested prompt: <auto-generated>
(c) Search the web for an image.
    ⚠ WEB-SOURCED IMAGES REQUIRE MANUAL USAGE-RIGHTS VERIFICATION
    BEFORE POSTING.
    Suggested keywords: <auto-generated>
(d) Skip this Key Point's visual anchor.
```

### Choice (a) — User provides

Polite exit. User adds image, re-runs.

### Choice (b) — Codex built-in `$imagegen`

Invoke Codex's native `image_gen` tool. Uses your ChatGPT plan
allocation, NOT your API key. Save to
`~/.cdhai-linkedin-skill/cache/imagegen_<hash>.png`. Mark `source: "codex_imagegen"`, add to `ai_generated_disclosures`.

### Choice (c) — Web image search

```bash
python3 _helpers/web_image_search.py "<keywords>" --max 5
```

Returns 5 candidates with image_url, source_page, title. User picks one
by index. Download:

```bash
python3 _helpers/web_image_search.py "<keywords>" --download <N>
```

**Every web-sourced image triggers:**

1. **A red-bordered warning section at the top of `before_you_post.docx`**:
   > ⚠ **WEB-SOURCED IMAGES — VERIFY USAGE RIGHTS BEFORE POSTING.**

2. **Per-image entry** with source page URL, search query, manual rights-checkbox.

3. **A CRITICAL reviewer flag** if `usage_rights_verified: true` is missing in the manifest.

4. **The ship recommendation stays REVISE** until usage rights are confirmed.

### Choice (d) — Skip

Record the skip. Key Point appears in text only.

---

## Total image count requirement

After all phases complete:

- **At least 5 distinct images** assigned across Key Points.
- Fewer than 5 → prompt user.

---

## What ends up in `linkedin_post.docx`

Each Key Point's assigned image is **embedded inline** in the docx next to
the paragraph that covers that Key Point. The user previews the post by
opening the docx; what they see is approximately what LinkedIn will look
like.

---

## What ends up in `before_you_post.docx`

- **"Image picks" section** lists every assigned image with: Key Point anchored, source (user / PDF extract / `$imagegen` / web), match confidence (Tier 1 / Tier 2 scores), rationale, and any verify-before-posting flag.
- **"Diversity check" subsection** lists the final subject distribution and scene-type distribution, with a ✓ or ⚠ summary.
- **"Web-sourced images" warning section** appears at the very top (red banner) when any web image is used.
- **"AI-generated images" disclosure section** appears when `$imagegen` was used.

---

## Anti-patterns (do not do these)

- Do not assign an image to a Key Point based on filename. Filenames lie.
- Do not assume the first 5 images are best just because they are first.
- Do not silently accept partial matches. Flag them.
- Do not skip Tier 2 for named people unless Tier 1 ≥ 0.85.
- Do not skip the diversity check. A 3-of-5 single-subject distribution is a quality failure.
- Do not invoke `$imagegen` or `web_image_search.py` without first asking the user (Tier 3 menu).
- Do not call any deprecated helpers — `unsplash_search.py`, `dalle_generate.py`, `image_describe.py` were removed in v0.4.1 / v0.4.2.
- Do not mark a web-sourced image as cleared for posting unless the user has explicitly verified rights.
- Do not crop / re-encode / watermark user-provided images for the embedded copies.
- Do not call an external OpenAI API. v0.4.2 uses Codex's native multimodal capabilities for all vision and LLM work.
