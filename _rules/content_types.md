# Content Types

Nine content types covering the post categories CDHAI and peer institutions
(Stanford HAI, MIT Jameel, Wharton AI Lab) actually publish on LinkedIn.

Codex detects the type from the input materials. If detection confidence
is below 70%, Codex asks the user which type fits.

---

## Type catalog

| Type | When to use | Tone default | Length |
|---|---|---|---|
| `event_recap` | After an event happened — recap of what occurred, who spoke, what was learned | warm_professional | ~1,300 chars |
| `upcoming_event` | Before an event — announcement with CTA to register/attend | warm_professional | ~700 chars |
| `faculty_presentation` | A CDHAI faculty gave a talk, keynote, panel, or class guest lecture | warm_professional | ~1,000 chars |
| `research_published` | New paper, white paper, or report released | warm_professional | ~1,200 chars |
| `thought_leadership` | Op-ed style commentary on a current AI/health issue from CDHAI perspective | warm_professional | ~1,400 chars |
| `awards_grants` | Grant won, prize received, ranking achievement | warm_playful | ~600 chars |
| `people_announcement` | New faculty hire, student graduation, fellowship admission, milestone | warm_playful | ~750 chars |
| `partnership_announcement` | New corporate affiliate, MOU, industry collaboration | warm_professional | ~800 chars |
| `general` | Catch-all when none of the above fits | warm_professional | ~900 chars |

---

## Detection signals (for Codex)

Codex scans the input materials for these signals:

| Signal pattern | Likely type |
|---|---|
| Past-tense verbs + event name + date in past | `event_recap` |
| "Join us", "Register", date in future | `upcoming_event` |
| "[Faculty name] presented / gave keynote / spoke at" | `faculty_presentation` |
| "New paper", "we publish", paper title, journal name | `research_published` |
| Opinion framing, "What X means for Y", no specific event | `thought_leadership` |
| "Awarded", "won grant", "received", funding amount | `awards_grants` |
| "Welcome [name]", "congratulations to [name]", graduation, hire | `people_announcement` |
| "Partnership with", "MOU", "corporate affiliate", company name | `partnership_announcement` |
| None of the above match cleanly | `general` |

**Confidence rule**: if the highest-scoring type is <70% confident OR the top
two types are within 10% of each other → ASK the user. Don't guess.

---

## Length is automatic

The length column above is the **target**, not a hard cap. Codex produces a
single post sized to the type. If the user says "too long" or "too short" in
chat feedback, that's a memory event (see `_rules/memory_policy.md`), not a
reason to produce a second version up front.

LinkedIn 2026 algorithm research (van der Blom): longer posts work well IF
the dwell-time signal is strong. Don't pad; don't truncate. Hit the target
naturally based on the input richness.

---

## Tone defaults explained

The default tone per type reflects what peer institutions actually publish:

- **warm_professional** is the dominant LinkedIn voice for academic AI centers
  (~70% of Stanford HAI / MIT Jameel posts). Use this as baseline.
- **warm_playful** for celebrations — grant wins, graduations, anniversaries.
  More emoji density allowed (1-3 emoji); slightly more exclamation.
- **formal_serious** is rarely the right call for LinkedIn. Reserve for
  sensitive topics (e.g., privacy / ethics white paper release) or when the
  user explicitly requests it.

The user can override the default tone in any run. If overridden once, the
skill applies it for that run only (see memory policy three-path rule).
