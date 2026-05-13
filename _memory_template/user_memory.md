# User Memory

Formal rules accumulated from user feedback over time. The skill reads
this file on every run and applies rules in addition to the rules in
`_rules/` (which are repo-level defaults).

When you give the skill feedback in chat and choose "Save as permanent
rule", the skill translates your informal feedback into a formal rule
and appends it here. The log of all such translations lives in
`memory_change_log.md`.

---

## How rules are formatted

Each rule has:

```markdown
## Rule {N} (added YYYY-MM-DD)
{The formal rule, written in actionable language}

**Source**: {brief description of the user feedback that led to this rule}
```

Rules are applied in order — earlier rules take precedence in case of
conflict. Rules cannot override `permission_policy.md` or `brand_rules.md`.

---

## Examples (these are illustrative — your file starts empty)

### Rule 1 (added 2026-05-13) — example, not active

Never open a post with "excited to announce", "thrilled to share", or
"delighted to inform". Use a concrete hook instead — the question the
content addresses, the unexpected finding, or the moment that mattered.

**Source**: user feedback during the May 2026 CHEETAH recap draft —
"stop using excited to announce, it sounds like every other LinkedIn post"

### Rule 2 (added 2026-05-15) — example, not active

When mentioning the CDHAI co-directors, list Ritu Agarwal and Gordon Gao
in alphabetical order by first name.

**Source**: user feedback during a grant-win post draft

---

## Your rules

(Empty — your rules will be appended below as you save them.)
