# LinkedIn Post Template

This is the structural template Codex fills in for every generated post.
The skill produces markdown matching this structure, then `_helpers/build_docx.py`
converts to `linkedin_post.docx`.

DO NOT include the metadata header (`---` block) in the final LinkedIn
text. The metadata is for reference in the .docx file only — when the user
copies-pastes to LinkedIn, they should select only the body + hashtags.

---

## Canonical structure

```markdown
---
**Content type**: {detected_type}
**Tone**: {applied_tone}
**Target length**: ~{target_chars} chars
**Generated**: {timestamp}
---

{HOOK — first 2 lines, strong opener, no LinkedIn clichés}

{BODY PARAGRAPH 1 — main substance, concrete and specific}

{BODY PARAGRAPH 2-3 — supporting details, names, specifics, numbers}

{CLOSING — single line or short paragraph; what to do next OR what to take away}

{HASHTAGS — 3-5, default 4, mix of broad + niche + branded, PascalCase}
```

---

## Length guidance per content type

(These are targets, not hard caps. Codex aims for them naturally based on
input richness; no padding, no truncation.)

| Type | Target | Hook | Body | Close |
|---|---|---|---|---|
| event_recap | ~1,300 | 1 line, the moment | 2-3 paragraphs of substance | "Worth your time"-style line |
| upcoming_event | ~700 | The "why" not the date | 1 paragraph of what to expect | Clear CTA with date and link |
| faculty_presentation | ~1,000 | The question the talk addressed | 1-2 paragraphs of the argument | "Watch / read more here" link |
| research_published | ~1,200 | The finding in one line, with number | 2 paragraphs: methods, implications | Link to paper / summary |
| thought_leadership | ~1,400 | Unexpected claim | 3 paragraphs of argument | Provocation or call to discussion |
| awards_grants | ~600 | 🎉 + achievement in one sentence | 1 short paragraph of context | Credit to team |
| people_announcement | ~750 | Welcome / congrats + why this matters | 1-2 paragraphs about the person | Welcome to community |
| partnership_announcement | ~800 | Joint statement on shared goal | 1-2 paragraphs of what's coming | Joint hashtag |
| general | ~900 | Whatever the input suggests | Match the input rhythm | Match the input rhythm |

---

## Hook patterns by type

Filled in by Codex based on the inspiration corpus. Reference examples:

- **event_recap**: "What if a single conference could rewire how you think about AI in healthcare?"
- **upcoming_event**: "Calling AI+healthcare experts! We're hosting our first..."
- **faculty_presentation**: "What does it mean to build an AI-native company in 2026?"
- **research_published**: "Improved data on gentrification will enable cities to target anti-displacement measures more effectively..."
- **thought_leadership**: "It's no longer a question of whether LLMs will replace doctors..."
- **awards_grants**: "🎉 Huge congratulations to CDHAI on securing..."
- **people_announcement**: "We are excited to welcome Andrew Burton-Jones to..."
- **partnership_announcement**: "[Org] welcomes [Partner] to our corporate affiliate program..."

NEVER open with:
- "We're excited to announce..."
- "I am thrilled to share..."
- "Delighted to inform you..."
- "[Day of week], [date], at [time]..." (leading with logistics)

---

## Hashtag template

```
{broad_hashtag} {niche_hashtag_1} {niche_hashtag_2} {branded_hashtag}
```

Pool (Codex picks based on content):

- **Broad**: #AI · #HealthAI · #DigitalHealth · #HealthTech · #AIinMedicine
- **Niche**: #ClinicalAI · #MedicalAI · #HealthEquity · #AIEthics · #GenAI · #LLMsInHealth · #ResponsibleAI · #DigitalTransformation
- **Branded**: #CDHAI · #JHUCarey · #JohnsHopkins · #CHITA2026 · #SitHigh · #MSISAI

See `_rules/brand_rules.md` for the full hashtag policy.

---

## What the skill does NOT include in the post

- The metadata header (top `---` block) — that's only for the .docx file reference
- Section labels like "HOOK" or "BODY" — those are template scaffolding
- URLs in the body of the post — LinkedIn penalizes external links in the
  post body; if a link is needed, it goes in the first comment per
  LinkedIn 2026 algorithm research
- Logistics like "date / time / location" in the hook
- Self-deprecating phrases ("just my two cents", "sorry for the long post")
- Buzzword stacks (see `linkedin_style.md` density rule)
