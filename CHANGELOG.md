# Changelog

## v0.4.4 — 2026-05-17

### What changed vs v0.4.3

After v0.4.3 shipped, the owner hit a real-world friction case: the
hard template gate refused to run when fields contained legitimate
placeholders like "NA" or empty notes. The trade-off was reconsidered.

**Template validator is now a SOFT diagnostic** (`validate_template.py`
always exits 0 unless the folder itself is unreadable). It still
classifies each of the six fields as `filled` / `sparse` / `missing`
and writes the findings to
`~/.cdhai-linkedin-skill/cache/template_validation.json`. Phase 9
reads that JSON and prominently surfaces sparse/missing fields in the
Audit Log + Must-Verify sections of `before_you_post.docx`. The user
can still see exactly what got inferred — they just aren't blocked.

**Reviewer gate stays HARD** (`reviewer_check.py` unchanged). This is
the contract that prevented the v0.4.2 team-member regression, and the
trade-off there is different: the cost of false positives is low
(reviewer always should run), while the cost of false negatives is
high (writer doing inline self-review → quality collapses).

### Rationale (the asymmetry, stated plainly)

Template input is user-controlled and varies legitimately. NA is a
valid answer. Hard-blocking on NA forces users to either lie ("Notes:
keep it short, also no special notes") or give up. Soft + report is
strictly better: the user gets their draft, and they see the gaps.

Reviewer execution is system-controlled and should not vary. Skipping
the reviewer is never a legitimate state. Hard-blocking on missing
reviewer flag has no false-positive cost — if Codex ran the sub-agent
correctly, the flag exists.

### Files changed

```
_helpers/validate_template.py    ← rewritten as soft diagnostic
SKILL.md                          ← Contracts section restructured;
                                    Phase 1 / Phase 9 / Constraints updated
VERSION                           ← 0.4.3 → 0.4.4
CHANGELOG.md                      ← this entry appended
```

### Migration

Existing v0.4.3 users: pull main, run `bash install.sh` (idempotent —
safe). No memory file changes required.

---

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
   fired.
3. **Empty memory.** New installs started with an empty
   `user_memory.md`. Team baseline rules existed only in the original
   author's accumulated memory and did not travel with the skill.

### What changed

- **Added `_helpers/validate_template.py`.** Hard exit on missing
  template fields. (Softened in v0.4.4.)
- **Added `_helpers/reviewer_check.py`.** Hard exit if the reviewer
  sub-agent did not write its flag file.
- **Audit Log section.** Every `before_you_post.docx` must include an
  Audit Log recording which contracts passed and which were bypassed.
- **Starter `user_memory.md`.** New installs receive a CDHAI team
  baseline.
- **Removed RITU AGARWAL uppercase rule.** Standard title case for all
  names.
