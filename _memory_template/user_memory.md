# user_memory.md

> **What this is:** persistent preferences this skill applies on every
> run. Translated from user feedback ("translate-before-save" pattern),
> not raw quotes.
>
> **How it gets here:** the skill writes new rules here when the user
> says "save permanently" in response to a feedback prompt. The starter
> entries below ship with v0.4.3 as the CDHAI team baseline; you can
> edit or remove them at any time.
>
> **Where this lives:** `~/.cdhai-linkedin-skill/memory/user_memory.md`

---

## CDHAI team baseline (v0.4.3 starter)

### Language
- Output language is English. Do not produce Chinese, Spanish, or other
  languages in the LinkedIn draft itself, even if user materials are in
  another language.

### People — Carey faculty naming
- Always use the "Professor" honorific on first mention for Carey faculty
  (e.g., "Professor Ritu Agarwal", "Professor Gordon Gao"). Subsequent
  mentions may use last name only.
- Use standard title case for names. Do not use all-caps for any person's
  name.

### Voice — anti-jargon
- Avoid corporate jargon and AI-cliché openers. Do not use:
  "leverage", "synergize", "best-in-class", "ambitious about",
  "clear-eyed about", "closer alignment", "at the intersection of",
  "unlock", "transformative", "game-changing".
- Prefer concrete verbs and specific nouns over abstractions.

### Voice — hook rules
- Do not open with "Last week", "Yesterday", or other time-relative
  phrasing. Always use absolute dates ("On May 8-9, 2026").
- Do not open with "I'm thrilled to / excited to / honored to".
- Open with a question, a specific fact, or a tension.

### Sessions and facts
- Only cite sessions, papers, names, and quotes that appear verbatim in
  the user-provided materials (Word template, agenda PDFs, papers).
- Do not infer session names from photographs, slides, or slido screens.
  If a slide is visible in an event photo, you may describe what the
  photo shows; you may not assert what the audience said, voted, or
  asked unless the user provided that information in writing.

### Hashtags
- Approved pool: `#SitHigh`, `#DigitalHealth`, `#HealthAI`,
  `#ResponsibleAI`, `#CHITA2026` (event-specific), `#CDHAI`.
- Plus up to one context-derived hashtag per post (e.g., `#GenerativeAI`
  if the post centers on gen AI specifically).
- Cap at 4 hashtags total. Place at the end of the post, lowercase
  prefixes, PascalCase for the rest.

### Image-text matching
- Captions must only describe what is verifiable in the image itself
  (people, scene, slide title visible on screen).
- Do not invent audience reactions, attendee names, or off-camera context
  in captions.

---

## User overrides

<!-- The skill appends new rules below this line when the user says
"save permanently". Do not edit the header above. -->
