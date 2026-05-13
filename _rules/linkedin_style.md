# LinkedIn Style Guidance

This file replaces the v0.2 "banned words" list. Peer institutions (Stanford
HAI, MIT Jameel) use words like "cutting-edge", "transforming", "robust" in
real published posts. Banning specific words produces stilted prose that
doesn't sound like CDHAI. Style judgment lives at the **density level**, not
the word level.

---

## How Codex chooses language

Codex learns voice from `_rules/inspiration_corpus.md` (real peer examples).
That's the primary mechanism. The bullets below are reminders, not rules to
enforce mechanically.

### Prefer

- Concrete over abstract — "Sybil predicts lung cancer risk 6 years ahead"
  beats "transformative cancer detection technology"
- Specific names over generic descriptors — "Marzyeh Ghassemi's group" beats
  "leading researchers"
- One claim per sentence — let the work do the work
- Active voice for human actions — "The team built X" not "X was built"
- Numbers when available — "85% accuracy on USMLE" beats "high accuracy"

### Use sparingly (not banned, just don't pile up)

These words are common and sometimes apt. They become problems only when
several appear close together. Use one or two if natural; don't write a
paragraph built on them:

`leverage` · `unlock` · `transform` / `transformative` · `revolutionary` ·
`cutting-edge` · `seamless` · `game-changing` · `world-class` · `synergize` ·
`disrupt` · `paradigm` · `passionate` · `excited to announce` · `delighted
to share` · `best-in-class`

### Legitimate technical terms (keep without flag)

- `robust` — standard in statistics, ML, software
- `novel` — academic standard
- `significant` — statistical or substantive meaning

---

## Density check (Reviewer skill applies this)

The companion reviewer skill (`cdhai-content-reviewer.skill`) flags a post
when hype-word density exceeds a threshold. Default heuristic:

> If a 200-character window contains 3+ words from the "use sparingly" list,
> flag that stretch for human review with severity = `warning`.

The reviewer does NOT auto-edit. It only flags. The human decides whether
the density is intentional (e.g., a grant-win celebration legitimately uses
several superlatives) or actually over-hyped.

---

## Emoji policy

Peer institutions use emoji visibly (MIT Jameel uses many: 🎊 🫁 🏥 🦠;
Stanford HAI uses fewer: 🚀 🩺). CDHAI's own grant-win post used 🎉.

Rule: **0-3 emoji per post, placed at content milestones, never decorative**.

Examples of OK placement:
- 🎉 at the open of a grant-win post
- 🔬 marking a research-result section
- 👏 at the close of a people_announcement

Don't use:
- Emoji in every paragraph
- Decorative emoji that don't add meaning (✨ 💫 🌟 strings)
- Emoji in formal_serious posts

---

## Opening hooks

LinkedIn's algorithm weighs the first 2 lines heavily (the "see more" cutoff).
Strong openings vary by type:

| Type | Hook pattern |
|---|---|
| event_recap | Concrete moment or unexpected line from the event |
| upcoming_event | The why, not the logistics — "What does AI in healthcare actually look like? Find out May 14." |
| faculty_presentation | The question the talk addressed |
| research_published | The finding in one line, with a number if possible |
| thought_leadership | A claim the reader doesn't expect |
| awards_grants | The achievement in one sentence — "🎉 CDHAI just won a $X grant to..." |
| people_announcement | Welcome / congratulations + the why this matters |

Don't open with: "We're excited to announce", "I am thrilled to share",
"Delighted to inform you" — these are LinkedIn clichés that lose attention
before "see more".

---

## Hashtag policy (see also brand_rules.md)

3-5 hashtags, default 4. Placement at end of post, never in hook. Mix:
- 1 broad (`#AI`, `#HealthAI`, `#DigitalHealth`)
- 1-2 niche (`#ClinicalAI`, `#HealthTech`, `#AIEthics`, `#MedicalAI`)
- 1 branded / event-specific (`#CDHAI`, `#JHUCarey`, `#CHITA2026`, `#SitHigh`)
