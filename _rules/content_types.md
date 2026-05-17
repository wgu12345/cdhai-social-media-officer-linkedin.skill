# Content Types

v0.4 change: the user picks Post Type in the content template. The skill
does NOT auto-detect. This file defines the **defaults** for each type:
target length, default tone, default hashtag composition, and structural
template.

The user can override the default tone in chat.

---

## The nine types

### 1. `event_recap`

A post recapping a recently-held event (conference, panel, talk, summit).

- **Default tone**: warm_professional
- **Target length**: 1,200-1,400 characters
- **Hashtags**: event tag (highest priority) + topic + branded
- **Structure**: question hook → what happened → who spoke → what was discussed → why it mattered → thanks → hashtags
- **Tense check**: Event Date must be in the past, ideally within 14 days.

### 2. `upcoming_event`

A save-the-date or invitation.

- **Default tone**: warm_professional
- **Target length**: 700-900 characters
- **Hashtags**: event tag + topic + branded
- **Structure**: hook (the question the event will address) → date and location → key speakers → who should come → registration link → hashtags
- **Tense check**: Event Date must be in the future.

### 3. `faculty_presentation`

A CDHAI faculty member is presenting at an external venue.

- **Default tone**: warm_professional
- **Target length**: 800-1,000 characters
- **Hashtags**: topic + branded + venue tag if applicable
- **Structure**: framing of the topic → faculty name and what they're presenting → when and where → why the topic matters → hashtags

### 4. `research_published`

Announcement of a new paper / publication. Triggers Phase 3 (paper analysis).

- **Default tone**: warm_professional
- **Target length**: 800-1,200 characters
- **Hashtags**: research topic + methodology tag + branded
- **Structure**: question the paper addresses → authors → headline finding → methodology one-liner → implication → link to paper → hashtags

### 5. `thought_leadership`

CDHAI commentary on a topic in the news or in the field.

- **Default tone**: formal_serious by default; user often overrides to warm_professional
- **Target length**: 1,200-1,400 characters
- **Hashtags**: topic + opinion-tag (#CDHAIperspective) + branded
- **Structure**: hook on the topic → CDHAI's framing → supporting evidence (from CDHAI work) → forward-looking statement → hashtags

### 6. `awards_grants`

Funding wins, prizes, formal recognitions.

- **Default tone**: warm_playful
- **Target length**: 600-900 characters
- **Hashtags**: branded + funder tag if applicable + topic
- **Structure**: warm celebration → the award details → what it enables → who's leading → hashtags
- **One emoji acceptable** (🎉 or 🏆) in this category only.

### 7. `people_announcement`

New hire, promotion, milestone, graduation.

- **Default tone**: warm_playful
- **Target length**: 500-800 characters
- **Hashtags**: branded + topic of the person's work
- **Structure**: welcome / congratulation → who they are → what they bring → looking forward → hashtags

### 8. `partnership_announcement`

CDHAI announces a collaboration with another institution / company.

- **Default tone**: warm_professional
- **Target length**: 800-1,000 characters
- **Hashtags**: branded + partner tag + topic
- **Structure**: announcement → who the partner is → what we'll work on together → why this combination matters → hashtags
- **Flag**: partnership posts often require sponsor / partner clearance before publishing. The reviewer skill always flags partner mentions for verification.

### 9. `general`

Catch-all for anything that doesn't fit the above eight.

- **Default tone**: warm_professional
- **Target length**: 800-1,200 characters
- **Hashtags**: per content, default 4
- **Structure**: free-form, but must follow `linkedin_style.md` rules (question hook, specific anchors per paragraph, hashtags at end)

---

## Tones (three options)

| Tone | Use for | Example opener |
|---|---|---|
| `warm_professional` | most posts (≈70%) | "What does an AI-ready health system actually require?" |
| `warm_playful` | celebrations, milestones | "Three years in, and we're just getting started 🎉" |
| `formal_serious` | privacy, policy, ethics, major institutional statements | "On AI governance in clinical practice, we want to make our position clear." |

Distribution observed in 50-post peer corpus analysis: warm_professional
~70%, warm_playful ~25%, formal_serious ~5%.

The user can override the default tone in chat after seeing the first draft.

---

## Length is a guideline, not a hard cap

These character counts are observed averages for the corresponding type
in peer institution posts (Stanford HAI, MIT Jameel, Wharton AI Lab,
etc.). Skill aims for the target naturally based on input richness.

- If the user's Key Points provide enough substance for a longer post,
  go longer. LinkedIn 2026 algorithm rewards dwell time.
- If the Key Points are sparse, do not pad. A 600-character post that
  earns engagement beats a 1,200-character post that loses readers.

The reviewer flags drafts that are <60% of target (too thin) or >140% of
target (overlong).
