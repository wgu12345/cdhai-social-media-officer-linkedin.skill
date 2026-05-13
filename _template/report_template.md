# Report Template

Used by the skill to produce `report.docx` — the audit + posting-instructions
document that accompanies every generated post.

The structure below is the canonical layout. Codex fills in each section
based on what happened during the run.

---

```markdown
# Post Generation Report

**Project**: {folder_name}
**Generated**: {timestamp}
**Skill version**: cdhai-social-media-officer-linkedin v{version}
**Content type detected**: {content_type} (confidence: {pct}%)
**Tone applied**: {tone}
**Target length**: ~{chars} chars

---

## Ready to publish

Follow these steps to post to LinkedIn:

1. Open `linkedin_post_standard.docx` (next to this report)
2. Select all the post text → copy → paste into LinkedIn's "Create a post"
3. Upload the images listed below in the order shown — LinkedIn lets you
   pick 1-3 from the ranked list
4. Hashtags are already at the end of the post text — no separate action
5. Recommended posting window: Tuesday-Thursday, 9-11 AM ET
   (CDHAI audience peaks in this window per LinkedIn analytics norms)

**Compliance reminder**: This is a draft. Human review required before
publishing per CDHAI policy. Confirm faculty names, dates, numbers, and
any quoted statements.

---

## Recommended images (ranked)

The skill found {N} images and ranked them by relevance. Pick 1-3 for the
final LinkedIn post.

| Rank | Filename | Why this rank | Suggested placement |
|---|---|---|---|
| 1 | image_05.jpg | Strongest match — shows keynote speaker mentioned in paragraph 2 | Banner |
| 2 | image_12.jpg | Audience shot from the event referenced in paragraph 3 | Inline |
| 3 | image_03.jpg | DC tech corridor visual referenced in closing | Inline |
| 4 | image_07.jpg | Conference logo / branded backdrop | Optional |
| ... | ... | ... | ... |

Top 10 shown if {N} ≥ 10. All shown if {N} < 10.

---

## What changed during generation

Edits the skill made automatically (per brand rules + user memory):

- "MSAI" → "MS-AI" (3 occurrences, brand rule)
- "Hopkins" → "Johns Hopkins" on first mention (brand rule)
- {other auto-fixes}

If you didn't want one of these changes, tell the skill in chat:
> "actually keep MSAI as-is for this run"
The skill will ask: this run only, or save as permanent rule?

---

## Items flagged for human verification

Things the skill couldn't confirm from the input materials. Verify before
publishing.

- WARNING: Speaker name "Dr. Yang" — first name not provided in input.
  Likely "Andrew Yang" based on context. Confirm.
- WARNING: Date "yesterday" appears in paragraph 1 — anchor date not in
  input. Confirm intended date.
- SUGGESTION: Closing line uses "transformative" + "cutting-edge" within
  150 chars — high hype density. Consider one removal.

(Severity levels: CRITICAL = must fix before posting; WARNING = verify;
 SUGGESTION = optional polish.)

---

## AI-generated images used

(Only present if DALL-E was invoked. Omit section otherwise.)

- image_07_dalle.png — generated prompt: "{prompt text}"
  Used in: {placement description}

Per JHU social-media guidelines, AI-generated images should be disclosed.

---

## Items needing human research

The skill identified gaps it couldn't fill. Provide additional information
on the next run if you want these incorporated:

- Speaker affiliation not in input materials — could enrich the post
- No quote from organizer — adding one would strengthen credibility

---

## Memory updates this run

(Filled if user feedback was processed during the run.)

- Path 2 (this run only): "include Andrew Burton-Jones" — applied to this
  draft, not saved as rule
- Path 3 (permanent): "stop opening with 'excited to announce'" → added to
  user_memory.md as Rule N

---

## Reviewer findings

(If the companion `cdhai-content-reviewer.skill` ran on this draft.)

See `review_report.docx` for the full review pass.

Summary: {N} critical · {N} warnings · {N} suggestions
```
