# Memory Policy

How the skill handles user feedback across three distinct paths.

---

## The three paths

When a user gives feedback in chat (e.g., "the post sounds too corporate",
"make the hook shorter", "always include a CTA at the end"), the skill
asks: **how should I handle this?** Three options:

### Path 1: Decline (`不存`)

**The user picks Decline when**: the feedback was a passing comment, an
exploration ("just curious if you could..."), or something they decided
against.

**Skill behavior**:
- Do not apply the change
- Do not record anything anywhere
- Continue with the original draft

This is the safe default when the user is ambiguous. Better to under-record
than to pollute memory with noise.

### Path 2: This run only (`临时`)

**The user picks This-run-only when**: the feedback is a one-off correction
for the current draft that shouldn't carry forward. Example: "for this
CHEETAH recap, mention Andrew Burton-Jones" — relevant once, not a rule.

**Skill behavior**:
- Apply the change to the current draft
- Log the change in `report.docx` under "Changes made this run"
- **Do NOT** write to `~/.cdhai-linkedin-skill/memory/user_memory.md`

The change has an audit trail (report.docx) but doesn't affect future runs.

### Path 3: Save as permanent rule (`永久`)

**The user picks Save-permanent when**: the feedback is a pattern that
should apply to every future post. Example: "we never use the phrase
'excited to announce'" — that's a durable rule.

**Skill behavior**:
1. Apply the change to the current draft
2. Log the change in `report.docx`
3. **Translate the informal feedback into a formal rule**
4. Append the formal rule to `~/.cdhai-linkedin-skill/memory/user_memory.md`
5. Append a log entry to `~/.cdhai-linkedin-skill/memory/memory_change_log.md`
   with: timestamp, user verbatim, translated rule

Future runs read `user_memory.md` and apply the rule automatically.

---

## Translation principle (Path 3 only)

User feedback is informal. The rule that goes into `user_memory.md` must
be formal and unambiguous so future Codex sessions apply it correctly.

| User feedback (informal) | Translated rule (formal) |
|---|---|
| "Don't make it sound corporate" | Avoid hype words from the "use sparingly" list when 3+ would appear in a 200-char window. Prefer concrete and specific language. |
| "Stop using excited to announce" | Never open a post with "excited to announce", "thrilled to share", or "delighted to inform". Use a concrete hook instead. |
| "I want hashtags at the bottom" | Place all hashtags after the main content, separated by one blank line. Never in the hook or body. (This is already brand_rules.md default — no new rule needed.) |
| "Add more about students" | When content involves student work or student events, name the students specifically in the first half of the post and link to their LinkedIn profiles if provided in the source materials. |
| "Make Gordon and Ritu equal" | When mentioning faculty co-directors, list Ritu Agarwal and Gordon Gao in alphabetical order by first name. |

Translation rules:
1. State the behavior, not the preference ("Avoid X" not "I don't like X")
2. Specify the trigger condition ("when this happens, do that")
3. Be concrete — name lists, character counts, specific phrasings
4. Include the source: "(per user feedback YYYY-MM-DD)"

---

## Memory file format

`user_memory.md`:

```markdown
# User Memory

Formal rules accumulated from user feedback. Sorted by date added.
Highest-precedence rules at the top.

## Rule 1 (added 2026-05-13)
Never open a post with "excited to announce", "thrilled to share",
or "delighted to inform". Use a concrete hook instead.
(Source: user feedback during CHEETAH recap draft)

## Rule 2 (added 2026-05-15)
When mentioning faculty co-directors, list Ritu Agarwal and Gordon
Gao in alphabetical order by first name.
(Source: user feedback during grant-win post)

...
```

`memory_change_log.md`:

```markdown
# Memory Change Log

## 2026-05-13 14:22
- User said: "stop using excited to announce, it sounds like every other LinkedIn post"
- Translated to: Never open a post with "excited to announce"...
- Action: Added as Rule 1

## 2026-05-15 09:10
- User said: "make Gordon and Ritu equal"
- Translated to: When mentioning faculty co-directors...
- Action: Added as Rule 2
```

---

## Conflicts between memory and inspiration corpus

If a user-memory rule conflicts with the inspiration corpus voice:

**User memory wins.**

The user knows CDHAI's preferences better than the corpus. The corpus is
a starting point; user memory refines it over time.

Edge case: if a rule actively contradicts a brand rule in `brand_rules.md`
(e.g., user says "use 7 hashtags" — exceeds the LinkedIn hard cap of 5),
the skill flags the conflict to the user before saving:

> "You said 7 hashtags, but our LinkedIn hard cap is 5 to avoid the
> algorithm's spam filter. Save as 'always use 5 hashtags' instead,
> or keep the original 4 default?"

Don't silently override brand rules.
