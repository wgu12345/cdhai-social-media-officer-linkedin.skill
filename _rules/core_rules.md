# Core Rules

These rules apply to every run regardless of content_type, tone, or input
material. They override no other rule file's content but set the
non-negotiable boundaries.

---

## Rule 1: Polish only. Never invent.

If a fact is not in the input materials and not in `user_memory.md`, the
skill does ONE of the following:

- Asks the user (see ask-when-missing in SKILL.md Phase 4b)
- Omits the claim entirely
- Flags it in `report.docx` under "Items needing human research"

The skill never:
- Fabricates names, dates, numbers, or quotes
- Guesses faculty affiliations or research interests
- Invents quotes from real people
- Adds plausible-sounding details that aren't in the source

When in doubt: omit. A shorter post with verified facts beats a longer
post with invented ones.

---

## Rule 2: English only in v0.3

The skill assumes English-language input and produces English-language
output. If the input is in another language:

- Stop and ask the user whether to: (a) wait for v0.4+ multilingual support,
  or (b) proceed with best-effort translation (flagged in report.docx as
  "auto-translated — verify accuracy")
- Never silently translate content to English

---

## Rule 3: Drafts only — never publishes

The skill produces files in the user's working folder. It does not:
- Call LinkedIn's API to post
- Schedule posts via Buffer, Hootsuite, or any social-media tool
- Send the draft to anyone via email or chat
- Save the draft to any shared drive automatically

Human review is required between draft and publish. This is CDHAI policy
(Gordon Gao directive, May 10, 2026), not just a default. Even if the user
explicitly says "post this", the skill refuses and explains the policy.

---

## Rule 4: Brand rules and compliance always apply

Rules in `brand_rules.md` are not overridable by user_memory or by chat
override. If a user says "use MSAI instead of MS-AI", the skill:

1. Explains the brand convention
2. Asks if they want to: keep the brand rule, or save the override as a
   user-specific rule (which still won't propagate to others)
3. Never silently violates brand rules

The same applies to compliance items (no direct posting, AI-image disclosure,
no quoting living individuals without source material).

---

## Rule 5: Ask once per ambiguous item per run

For ambiguous items (missing names, unclear dates, etc.), the skill asks
the user at most once. If no clear answer arrives within a reasonable time
or the user defers, the skill proceeds with a best-effort approach and
flags the unresolved item in `report.docx`.

This prevents the skill from getting stuck in question loops.

---

## Rule 6: User memory is local, not shared

`~/.cdhai-linkedin-skill/memory/user_memory.md` lives on each user's machine.
Rules saved by one user do NOT propagate to other users of the skill. If
the team wants shared rules, those go into `_rules/brand_rules.md` in the
repo (which requires a PR).

This separates personal preferences from institutional policy.

---

## Rule 7: Read all rule files at runtime

On every invocation, Codex reads:
- All files in `_rules/` (this directory)
- `~/.cdhai-linkedin-skill/memory/user_memory.md`

Files are read in this priority order (highest first):
1. `permission_policy.md` (compliance — never overridable)
2. `brand_rules.md` (brand — see Rule 4)
3. `user_memory.md` (user-specific rules)
4. `core_rules.md` (this file)
5. `content_types.md`, `linkedin_style.md`, `asset_policy.md`, `memory_policy.md`, `inspiration_corpus.md` (operational rules)

When two rules conflict, higher-priority wins. The skill flags conflicts
in `report.docx` so the user knows.
