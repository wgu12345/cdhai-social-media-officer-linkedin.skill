# Inspiration Corpus

Real examples of LinkedIn voice from peer academic AI centers. Codex
references this corpus to learn what good CDHAI-style writing looks like
on LinkedIn.

This is the primary mechanism for style — it replaces the v0.2 banned-words
list. Match the corpus voice; let it teach the skill what to do.

**Future enhancement** (v0.4+): fetch live URLs to refresh the corpus
quarterly. For now, the descriptions below are sufficient.

---

## Tone distribution (analyzed May 2026)

Looking at ~50 recent posts across 6 peer institutions:

| Tone | Frequency | When used |
|---|---|---|
| **warm_professional** | ~70% | Default for research shares, event posts, faculty intros, opinion pieces |
| **warm_playful** | ~25% | Grant wins, anniversaries, graduations, holiday posts, retreat/social events |
| **formal_serious** | ~5% | Privacy / ethics white paper releases; major foundation grant announcements |

**Codex default**: `warm_professional` unless content_type triggers a
playful default (see `content_types.md`) or user explicitly overrides.

---

## Peer institution voice notes

### Stanford HAI (`linkedin.com/company/stanfordhai`)

- Tone: warm_professional, dry-ish, slightly understated
- Sentence length: short paragraphs, 1-3 sentences each
- Emoji: rare; only 🚀 🩺 for special moments
- Hashtags: 1-3, mix of broad and event-specific (#AIIndex2024)
- Hook style: questions ("What does human-centered design mean?"), or
  scholarly framing ("Stanford scholars use computer vision to study...")
- Avoids: hype words, exclamation marks, first person "I/we" hype

Sample opener:
> "Improved data on gentrification will enable cities to target
> anti-displacement measures more effectively, says Stanford HAI faculty
> member Jackelyn Hwang."

### MIT Jameel Clinic (`linkedin.com/company/aihealthmit`)

- Tone: mix of warm_professional and warm_playful (playful for milestones)
- Sentence length: medium paragraphs, occasionally longer for storytelling
- Emoji: visible and frequent for celebration posts (🎊 🫁 🏥 🦠 🎂 👏)
- Hashtags: 4-6 (slightly more than Stanford HAI)
- Hook style: warm opening for celebrations ("🎊 2023 was an incredible
  year"), question-led for research ("How did prescription drugs get
  so expensive?")
- Uses lowercase camelCase hashtags: `#aiforgood #aiforhealth`

Sample opener (playful):
> "🎊 2023 was an incredible year, not just for AI research but also as a
> milestone marking the 5th anniversary of MIT Jameel Clinic - AI & Health 🎂"

Sample opener (professional):
> "Today marks our 5-year anniversary as MIT Jameel Clinic..."

### Wharton AI Lab / HBS / Yale Digital Ethics / JHU CIL

- Generally follow Stanford HAI's restrained tone
- Few emoji
- Heavier on data points and citations
- Hashtags: 2-4

### CDHAI's own posts (via Carey's LinkedIn)

- Carey corporate account writes most CDHAI mentions
- Tone: warm_professional with 🎉 for celebrations
- Hashtags: 3 (Carey's website policy — but LinkedIn norm is 3-5,
  so the skill defaults to 4)
- Voice: institutional, names dropped (faculty + co-directors)

Example (CDHAI grant win, from Carey's account):
> "🎉 Huge congratulations to the Carey Business School's Center for
> Digital Health and Artificial Intelligence (CDHAI) on securing a
> groundbreaking grant! This well-deserved grant highlights Carey's
> pivotal role as a driving force within the Hopkins initiative..."

---

## What this corpus is NOT

- Not a list of forbidden words (see `linkedin_style.md` for why)
- Not a rigid template — Codex synthesizes voice, doesn't copy phrasing
- Not exhaustive — when in doubt, write closer to Stanford HAI's restraint
  than to PR-style hype

---

## How Codex should use this corpus

1. Before generating any post, read this file in its entirety
2. Match the voice closest to the detected `content_type` and `tone`
3. Don't quote or near-quote any sample text — synthesize
4. When uncertain about a word choice, ask: "would Stanford HAI publish
   this phrasing?" If no, rewrite.
