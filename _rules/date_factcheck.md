# Date Fact-Check

The skill knows today's date from the runtime environment. It uses this
to verify date-anchored claims and to compute natural-language time
references in the post.

---

## Inputs

- **Today's date**: from system time when the skill runs.
- **Event Date**: from the user's content template (required field).
- **Dates in source materials**: any date string found in supporting PDFs (especially conference agendas, paper publication dates, press release dates).

---

## Phase 2 checks

### Check 1 — Event Date format and validity

- Parse the user's Event Date. Acceptable formats:
  - YYYY-MM-DD
  - Month DD, YYYY
  - DD Month YYYY
- If unparseable → ask the user to clarify.
- If the year is missing → ask.
- If the date is impossible (Feb 30) → ask.

### Check 2 — Today vs Event Date

Compute the difference and pick the right tense:

| Difference | Tense / phrasing |
|---|---|
| Event > 14 days in the future | "On <Month DD>" |
| Event 1-14 days in the future | "<Day-of-week>, Month DD" or "next <day-of-week>" |
| Event is today | "Today" |
| Event was yesterday | "Yesterday" |
| Event 2-14 days ago | "<Day-of-week>" or "earlier this week" / "last week" |
| Event 15-60 days ago | "<Month DD>" |
| Event > 60 days ago | "<Month YYYY>" |

### Check 3 — Post Type ↔ tense consistency

| Post Type | Expected tense |
|---|---|
| `event_recap` | Past — event must be ≤ ~30 days ago |
| `upcoming_event` | Future — event must be in the future |
| `research_published` | Past or just-published |
| `awards_grants` | Recent past or just-received |
| `people_announcement` | Past, present, or near future |
| `partnership_announcement` | Recent past or just-announced |
| `faculty_presentation` | Past or future depending on whether recap or invitation |
| `thought_leadership` | No date dependency |
| `general` | No date dependency |

If Post Type and Event Date are mismatched → **flag in report**:

> Post Type is "event_recap" but the Event Date is 14 days in the future.
> If this is a recap, the date is wrong. If this is an upcoming event,
> change Post Type to "upcoming_event".

### Check 4 — Cross-reference against supporting PDFs

For every date string found in supporting PDFs (especially conference
agendas), compare against the user's Event Date.

If they disagree → flag as a date conflict:

> The user template says Event Date: April 28-29, 2026.
> The agenda PDF "CHITA_2026_program.pdf" says May 8-9, 2026.
> The draft is being produced WITHOUT dates pending resolution.

Omit dates from the draft when there is a conflict. Surface the conflict
in `before_you_post.docx` under "Must verify".

### Check 5 — Bizarre temporal claims in source notes

Scan the Background / Notes fields for natural-language time references:

- "yesterday at the conference" — verify against Event Date.
- "next Tuesday" — compute the actual Tuesday and verify.
- "during last week's panel" — verify.

Any reference that disagrees with the Event Date → flag and ask user.

---

## What appears in the post

The post uses the **computed natural-language reference** from Check 2,
not the raw user input. If the user wrote "April 28-29, 2026" and that's
3 days ago when the skill runs, the post says:

✅ "Earlier this week at CHITA 2026..."
❌ "On April 28-29, 2026, CHITA..."
❌ "April 28, 2026 saw the launch of..."

LinkedIn audiences read posts when they appear in feed. Calendar dates
are usually less natural than relative time markers.

**Exception**: `upcoming_event` posts always use the calendar date so
readers can put it in their calendars:

✅ "Save the date — CHITA 2026, May 8-9 in Washington, DC."

---

## What appears in `before_you_post.docx`

A "Date verification" subsection of the report records:

- The user's stated Event Date
- Today's date when the skill ran
- The computed natural-language reference used in the post
- Any cross-reference conflicts found
- Any tense / Post Type mismatches found

This gives the user explicit traceability of how the skill handled time.
