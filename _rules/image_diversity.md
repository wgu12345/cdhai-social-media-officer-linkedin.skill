# Image Diversity Constraints (v0.4.2)

Why this rule exists: real folders often have skewed photo distributions.
Gordon attended the event so there are 10 photos of him. Other speakers
have 2 photos each. Without a diversity constraint, the matching system
would pick 3 Gordon photos out of 5 — boring, visually repetitive, and
unfair to other Key Points.

This rule sits on top of `image_matching.md` Tier 1/2/3 scoring.

---

## Two diversity dimensions

### Dimension A — Subject diversity

A "subject" is a specific named person or a clearly defined group.
Examples:
- "Gordon Gao" — a specific named person
- "Conference audience" — a defined group (the audience, not a specific person)
- "Empty podium" — no subject

**Constraint:** In a final set of 5 selected images, **no single named
person appears in more than 2 images** (40% cap). If 6 images, cap is 2;
if 7-9 images, cap is 3 (still ~35% cap); if 10+, cap scales linearly.

### Dimension B — Scene-type diversity

Scene types (from Tier 1 description's `setting` field):
- `indoor_podium`, `indoor_panel`, `indoor_classroom`, `indoor_lab`,
  `indoor_reception`, `indoor_office`, `outdoor_campus`, `outdoor_other`,
  `screenshot`, `document`, `unclear`

**Constraint:** In a final set of 5 selected images, **no single scene
type appears more than twice**. Mix podium / panel / reception / lab,
etc. for visual variety.

---

## Per-Key-Point uniqueness

Every Key Point should be anchored by a **different image**. The same
image rarely makes sense as the anchor for two different Key Points.

Exception: if a single image genuinely captures multiple Key Points
(e.g., a group shot showing both Gordon AND Ritu, both named in
different Key Points), it MAY anchor both — but then it counts toward
the diversity caps for both subjects.

---

## Diversification algorithm

Codex runs this AFTER Phase 5 (Key Point ↔ Image matching) and BEFORE
Phase 6 (Tier 3 fallback):

### Step D1 — Tally

For the current set of assigned images:
1. Count occurrences of each named subject across selected images.
2. Count occurrences of each scene type across selected images.
3. Identify violations (any subject or scene exceeding its cap).

### Step D2 — If a violation exists, rebalance

For each violating subject (e.g., Gordon appears in 3 of 5 picks):

1. **Rank** the Gordon-anchored picks by match confidence (highest first).
2. **Keep** the top N (where N = the cap, e.g., 2).
3. **Release** the lowest-confidence Gordon picks from their Key Points.
4. **Re-match** those released Key Points using:
   - **a.** Other candidate images that scored ≥ 0.5 but lost to a Gordon pick
   - **b.** Images of *other* people that match the Key Point semantically (e.g., another panelist who could anchor the same theme)
   - **c.** Scene-type images that fit the topic but feature different subjects
5. **If no alternative scores ≥ 0.5** → trigger Tier 3 fallback for that Key Point.

Same algorithm applies to scene-type violations.

### Step D3 — Recheck

Re-tally after rebalancing. If still violating (rare), prompt the user:

> Your folder is heavily skewed toward photos of <name>. After balancing,
> N Key Points still lack diverse visuals. Options: (a) add more varied
> photos and re-run, (b) accept the imbalance, (c) use Tier 3 fallback
> for the unmatched Key Points.

---

## Worked example

User folder: 12 images.
- 8 are of Gordon (podium shots, networking shots, panel shots)
- 2 are of Ritu (one panel, one keynote)
- 1 is a wide audience shot
- 1 is a coffee-break candid (no main subject)

Key Points:
1. "Gordon Gao's keynote on AI in clinical decision support"
2. "Ritu Agarwal's panel on equity in healthcare AI"
3. "Cross-disciplinary attendance from MD/PhD students and faculty"
4. "Hands-on workshop with industry partners"
5. "Looking forward to next year's CHITA conference"

Initial Tier 1/2 matching (without diversity):
- KP1 → Gordon-podium-A (0.92, named-person Tier 2)
- KP2 → Ritu-keynote (0.88, named-person Tier 2)
- KP3 → Audience-wide (0.71, Tier 1)
- KP4 → Gordon-panel-B (0.76, second-best after no workshop photos)
- KP5 → Gordon-networking-C (0.62, weak match — closest "forward-looking" feel)

Initial subject tally: Gordon=3, Ritu=1, Audience=1. **VIOLATION** (Gordon over 2/5 cap).

Diversification:
- Keep Gordon's top 2 picks: Gordon-podium-A (KP1, 0.92) and Gordon-panel-B (KP4, 0.76)
- Release Gordon-networking-C from KP5
- Re-match KP5: no good alternatives in folder → trigger Tier 3 for KP5

Final after Tier 3:
- KP5 → user picks "search the web for a CHITA-2027-themed visual" → web image (with usage-rights warning)

Final subject tally: Gordon=2, Ritu=1, Audience=1, Web=1. ✓ No violation.

---

## Hard rules

- **Always run the diversification algorithm before declaring final picks.**
- **Never silently accept a violation.** Either rebalance or surface to user.
- **Diversification preserves the highest-confidence pick for each subject** — we keep the best Gordon photo, not the worst.
- **Diversification never sacrifices a high-confidence Tier 2 face match** for a low-confidence Tier 1 alternative. If Gordon-podium-A scored 0.92 and the alternative scored 0.41, keep Gordon and rebalance somewhere else.
- **Group shots that cover multiple Key Points** are recorded in the manifest as anchoring all the Key Points they cover; their subject tally counts toward each named person visible.

---

## What appears in `before_you_post.docx`

In the "Image picks" section, each pick lists:
- The Key Point it anchors
- The match confidence
- **The subject and scene type** (so the user can verify diversity at a glance)

A "Diversity check" subsection summarizes:
- Final subject distribution: "Gordon × 2, Ritu × 1, Audience × 1, Other × 1"
- Final scene-type distribution: "podium × 2, panel × 1, audience × 1, web × 1"
- "✓ Diversity constraints satisfied" or "⚠ One subject exceeds cap — see Image picks"
