# Paper Analysis — Level 3 Spec

When the user wants to announce a research paper, the skill performs full
analysis of the paper PDF. This is the v0.4 implementation of Gordon's
vision: drop in a paper, get a post.

---

## When to trigger paper analysis

EITHER condition triggers paper analysis mode:

1. The user's `Post Type` field in the content template is `research_published`.
2. The folder contains a PDF whose filename or first page suggests it is a research paper:
   - Title-cased title in large type on page 1
   - "Abstract" header within first two pages
   - Author list with affiliations within first two pages

If both conditions are true, definitely a paper run.
If only condition 2 is true but Post Type is set to something else, ask
the user: "I see a research paper in your folder, but Post Type is set to
`<other>`. Should I treat the paper as primary content or as supporting
material?"

---

## Phase 3a — PDF text extraction (deterministic helper)

Run:
```bash
python3 _helpers/pdf_paper_extract.py <paper.pdf>
```

The helper uses `pypdf` to extract raw text only. It returns JSON:

```json
{
  "_meta": {
    "path": "...",
    "filename": "...",
    "page_count": 38,
    "chunk_count": 5,
    "is_likely_research_paper": true,
    "signals": {
      "has_abstract_header": true,
      "has_keywords_header": true,
      "has_doi": true,
      "has_university_in_first_page": true
    }
  },
  "first_two_pages": "<raw text from pages 1-2>",
  "full_text_chunks": ["<chunk 0>", "<chunk 1>", ...]
}
```

**The helper does NOT do any LLM analysis.** It is pure text extraction.
Codex analyzes the returned text directly.

---

## Phase 3b — Codex analyzes the extracted text

You (Codex) read the helper's output and produce two structured outputs:

### Metadata extraction

Read `first_two_pages`. Produce JSON, no other text:

```json
{
  "title": "string or null",
  "authors": [{"name": "string", "affiliation": "string or null"}],
  "abstract": "verbatim abstract text or null",
  "keywords": ["array or empty"],
  "venue": "journal / conference / 'Working paper' / null",
  "doi": "DOI string or null",
  "publication_date": "YYYY-MM or YYYY-MM-DD or null"
}
```

Rules:
- Title is the prominent title text at the top of page 1.
- Authors in order as printed; affiliations from footnotes / superscripts.
- Abstract is the section labeled "Abstract".
- If a field is genuinely absent → return `null`. Do not fabricate.

### Substance extraction

Read `full_text_chunks`. Produce JSON, no other text:

```json
{
  "key_findings": [
    {"finding": "string", "source_chunk_index": <integer>}
  ],
  "methodology_one_sentence": "...",
  "implications_one_sentence": "...",
  "limitations_one_sentence": "... or null",
  "audience_friendly_takeaway": "one paragraph"
}
```

Rules (hard):
- 3-5 key findings. Quote-like phrasing or close paraphrase.
- Every finding traces to a specific `source_chunk_index`.
- **Never strengthen claims beyond the paper.** "12% improvement" stays "12% improvement", never "massive improvement".
- **Never speculate beyond the paper.** If the paper does not claim X, do not add X.
- Stay close to the paper's framing in "implications".
- "audience_friendly_takeaway" must remain faithful but in plain language.
- If a field cannot be sourced → return `null`.

---

## Phase 3c — Author identification and faculty matching

For each author in the metadata, run the helper for **web search + photo
download only** (the comparison itself is Codex-native):

```bash
python3 _helpers/face_compare.py --identify "<author name>"
```

This returns a cached reference photo path. Codex then:

1. Reads the helper's JSON response.
2. If a cached photo was found → tag the author appropriately based on
   the source URL:
   - URL on `carey.jhu.edu/faculty` → `faculty_internal`
   - URL on `jhu.edu` or `hopkinsmedicine.org` not labeled faculty → `student_or_postdoc` (verify with the bio page text)
   - External URL → `external_collaborator`
3. If no photo found → tag `external_collaborator` (unfindable on JHU pages); the post uses plain name on first mention.
4. Save reference photo paths for use in Phase 5 Tier 2 (face comparison done by Codex looking at both images).

This tagging drives how the post addresses each author. Internal faculty
get "Professor X". Internal students get "X, PhD student in ...". External
collaborators get plain "X (Institution)".

---

## Phase 3d — Compose paper announcement content

When Phase 7 runs for a `research_published` post, the content generator
uses the paper bundle directly. The default structure for a paper
announcement is:

1. **Hook**: a one-sentence framing of the question the paper addresses. Use the paper's own framing where possible.
2. **Authors line**: "New paper by Professor X, Y, and Z."
3. **Headline finding**: the most user-friendly key finding, phrased for a LinkedIn audience.
4. **Methodology one-liner**: how the question was answered.
5. **Implication**: why this matters for clinicians / health systems / policymakers.
6. **Read more**: link to the paper if available (DOI, working paper URL, or "available on request").
7. **Hashtags**: per `brand_rules.md`.

**Length target**: 800-1,200 characters. Paper announcements should be
substantive but not academic-length.

---

## Anti-hallucination rules (paper-specific)

These are stricter than the general "ask-when-missing" rule because
research papers are public-facing and misquoting is worse than embarrassing.

1. **Never restate a key finding in stronger language than the paper itself**.
   - Paper: "We find a 12% improvement on average."
   - Post: ✅ "Average improvement of 12%."
   - Post: ❌ "Massive 12% improvement."
   - Post: ❌ "Across the board improvement."

2. **Never extend findings beyond their stated scope**.
   - Paper: "In our sample of 500 community hospitals..."
   - Post: ✅ "Across 500 community hospitals..."
   - Post: ❌ "Hospitals generally..."

3. **Never speculate about implications the paper does not claim**.
   - If the paper does not say "this could transform X", the post does not say it either.

4. **Always include limitations or scope qualifiers** if they appear in the abstract.

5. **Authors' names spell exactly as in the paper**, including all middle initials.

6. **Quote with quotation marks only verbatim text**. Paraphrase otherwise. Never use scare quotes ironically.

---

## Author co-authorship attribution

When a paper has many authors, the LinkedIn post:

- Names all CDHAI-affiliated authors with title.
- Names the first external collaborator and uses "and colleagues" or "and X others" for the rest, unless the user template specifies different handling.
- If a paper has only external authors but is being announced via CDHAI because of a research connection (e.g., a CDHAI seminar paper), the post says "Featured at CDHAI's <event>" and names the authors as external.

---

## Image matching for paper posts

In Phase 5, for paper posts:

- If a reference photo was fetched for an internal author in Phase 3c, use it for Tier 2 face comparison against any candidate images in the folder. A photo of the lead author = strong visual anchor for the post.
- If no candidate photo matches an author, fall through to Tier 3 (Unsplash search for the topic, or skip).
- A graph / chart / table image extracted from the PDF can also be used as a visual anchor for a key-findings paragraph. Tier 1 description will tag these as "figure_from_paper" and they score highly for paragraphs that discuss the corresponding finding.

---

## Output specifics

`before_you_post.docx` for a paper post includes additional sections:

- **Paper metadata box**: Title, Authors, Venue, DOI, Date.
- **Findings traceability**: each finding in the post mapped to a chunk index in the PDF.
- **Quoted material**: any direct quotes verified against source.
- **Author tagging**: internal vs external classification with link to bio pages.
