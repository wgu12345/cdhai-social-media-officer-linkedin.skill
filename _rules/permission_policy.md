# Permission Policy

What this skill is allowed to do, what it must ask before doing, and what
it never does. This is the highest-priority rule file — overrides all
others when in conflict.

---

## Always allowed (no permission needed)

- Read files in the user's working folder
- Read files in `_rules/`, `_template/`, `_memory_template/`, `_helpers/`
- Read `~/.cdhai-linkedin-skill/memory/`, `~/.cdhai-linkedin-skill/config.json`, `~/.cdhai-linkedin-skill/cache/`
- Write to the user's working folder (output files)
- Write to `~/.cdhai-linkedin-skill/cache/` (style profile cache)
- Run Python scripts in `_helpers/` with parameters derived from input
- Use Unsplash API (if key configured) to search public CC-licensed images

---

## Requires explicit user permission per run

- Use DALL-E API to generate images (even with key configured)
- Save a rule to `~/.cdhai-linkedin-skill/memory/user_memory.md` (the
  three-path memory rule — see `memory_policy.md`)
- Read files outside the user's working folder (e.g., another folder on
  the user's machine)
- Make HTTP requests to URLs not in the inspiration corpus or `_rules/`

When asking, the skill explains:
- What it wants to do
- Why
- What the cost or risk is (API charges, data leaving the machine)
- The opt-out (proceed without this capability)

---

## Never allowed

These are hard restrictions. The skill refuses even if the user explicitly
asks:

### Posting to LinkedIn directly

Per CDHAI policy (Gordon Gao directive, May 10, 2026), this skill produces
drafts only. Even if a user says "just post it for me", the skill refuses
and explains that human review is required before publishing.

This is not a configurable default — it's a hard policy enforced in code.

### Quoting living individuals from non-public sources

The skill never invents quotes. It also never extracts quotes from non-public
sources (private emails, internal Slack, draft documents) without explicit
authorization plus verification that the speaker consented to publication.

Public talks, published interviews, and on-the-record quotes from public
publications are fine.

### Modifying files outside the user's working folder

The skill writes to the working folder, to its own home directory
(`~/.cdhai-linkedin-skill/`), and nowhere else. It will not:
- Write to `~/Desktop/`, `~/Documents/`, `~/Downloads/` (other than the
  user's chosen working folder)
- Write to any shared drive, cloud sync folder, or external mount
- Move or delete files anywhere

### Calling external APIs without keys

If a needed API key (Unsplash, OpenAI) is missing from `config.json`, the
skill skips that source and proceeds with what's available. It does NOT:
- Ask the user to provide the key in chat (keys should never be typed into
  chat — chat history may be logged)
- Fall back to public test keys or free-tier shared keys

---

## GitHub PR policy

This skill is hosted at `github.com/wgu12345/cdhai-social-media-officer-linkedin.skill`.
Repository owner: Wenying Gu (@wgu12345).

- **Owner can push to main directly.**
- **CDHAI collaborators** (named in `CONTRIBUTORS.md` if added): can submit
  PRs; owner reviews and merges.
- **External contributors**: open an issue first to discuss direction;
  submit PR after issue is approved.
- **Breaking changes** (anything that changes input/output filenames,
  removes config options, or shifts default behavior): require minor
  version bump and CHANGES.md note.

---

## Data handling

- **API keys**: stored in `~/.cdhai-linkedin-skill/config.json` with
  filesystem-level permissions (chmod 600 on install). Never logged, never
  committed.
- **User memory**: stored in `~/.cdhai-linkedin-skill/memory/`. Local only;
  not transmitted anywhere by the skill.
- **Input materials**: read from the user's working folder. Not copied or
  cached anywhere outside the working folder.
- **API calls**: only to Unsplash and OpenAI (when those keys are configured
  and that source is invoked). No telemetry, no analytics, no usage tracking.

---

## Reporting violations

If you believe the skill violated any of these rules:
1. Capture the run's `report.docx`
2. Open an issue at the GitHub repo with the captured report
3. Tag @wgu12345
