# Changelog

## v0.4.3 — 2026-05-17

### The problem v0.4.3 fixes

A team-member install of v0.4.2 produced a measurably worse LinkedIn
draft than the author's own runs. Three contributing causes were
identified:

1. **Soft constraints.** SKILL.md's "Word template required" was a
   markdown rule, not a mechanical gate. When the team member's folder
   lacked a proper template, the skill first refused, then capitulated
   on the next turn and produced a sparse-input draft.
2. **Skipped reviewer.** The skill's "reviewer runs as Codex
   sub-agent" rule was treated as optional. The team-member run did
   in-line self-review only, which meant the 9 quality checks never
   fired. As a result, the draft contained:
   - a hallucinated slido poll opening ("doctors / patients / research /
     conference") not present on the actual slide,
   - a relative time phrase ("Last week") that the v0.4.2 reviewer
     would have flagged,
   - hashtags outside the approved pool,
   - corporate-feel-good language that hype-density would have caught,
   - a possibly mis-identified Ritu Agarwal photo.
3. **Empty memory.** New installs started with an empty
   `user_memory.md`. Team baseline rules (English-only, anti-jargon,
   approved hashtag pool, absolute-date opener) existed only in the
   original author's accumulated memory and did not travel with the
   skill.

### What changed

- **Added `_helpers/validate_template.py`.** Hard exit on missing
  template fields. SKILL.md Phase 1 now requires this script to pass
  before any draft work begins.
- **Added `_helpers/reviewer_check.py`.** Hard exit if the reviewer
  sub-agent did not write its flag file. SKILL.md Phase 9 now requires
  this script to pass before `linkedin_post.docx` is written.
- **Audit Log section.** Every `before_you_post.docx` must include an
  Audit Log recording which hard contracts passed and which were
  bypassed.
- **Starter `user_memory.md`.** New installs receive a CDHAI team
  baseline (language, naming, voice, hashtags, image-text matching
  rules). `install.sh` seeds it only if no user memory exists, so
  existing users are not overwritten.
- **Removed RITU AGARWAL uppercase rule.** Standard title case is now
  the rule for all names in starter memory; the v0.4.2-era uppercase
  experiment is dropped.

### Migration for existing v0.4.2 users

If your `~/.cdhai-linkedin-skill/memory/user_memory.md` contains a rule
like "RITU AGARWAL appears in uppercase", remove that line. Then
re-run `install.sh` from the v0.4.3 repo to pick up the new helpers.
Your accumulated memory is preserved.

### Files added

```
_helpers/validate_template.py
_helpers/reviewer_check.py
```

### Files updated

```
SKILL.md           (Hard Contracts section, Phase 1/8/9 edits, Constraints)
install.sh         (seeds starter memory; smoke-tests python-docx)
VERSION            (0.4.2 → 0.4.3)
_memory_template/user_memory.md   (starter baseline, no uppercase rule)
```
