# CDHAI LinkedIn Skill — Team Guide

For program coordinators, MarComm staff, postdocs, and anyone else on the
CDHAI team who needs to draft LinkedIn posts. No coding required.

This guide walks through:
1. One-time setup (15 minutes)
2. Day-to-day use (5 minutes per post)
3. Common situations and how to handle them
4. Where to ask for help

---

## One-time setup

### Step 1: Install Codex App

Codex is the desktop app that runs this skill. Download from
[OpenAI Codex](https://chatgpt.com/codex) (Mac and Windows supported).

After install, sign in with your OpenAI account.

### Step 2: Install this skill in Codex App

1. Open Codex App
2. Click **Plugins** in the left sidebar
3. Click **Install from URL** at the top right
4. Paste this URL: `https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill`
5. Click **Install**

Repeat for the reviewer skill: `https://github.com/wgu12345/cdhai-content-reviewer.skill`

The first install runs a setup script that creates a configuration folder
on your computer. This takes ~30 seconds.

### Step 3: (Optional) Configure API keys for image search

The skill can search Unsplash (free, royalty-free photos) and generate
images with DALL-E (paid, ~$0.04 per image). To enable these:

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type: `open ~/.cdhai-linkedin-skill/config.json` (Mac) or
   `notepad %USERPROFILE%\.cdhai-linkedin-skill\config.json` (Windows)
3. Fill in the keys:
   - `unsplash_access_key`: get free at [unsplash.com/developers](https://unsplash.com/developers)
   - `openai_api_key`: get at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (note: separate from your ChatGPT subscription)
4. Save and close

If you skip this step, the skill still works — it just won't offer Unsplash
or DALL-E as image sources. You'll need to provide your own images in the
folder.

---

## Day-to-day use

### Step 1: Make a folder for each post

Pick a location on your computer (Desktop is fine). Create a folder
named for the post.

Example: `~/Desktop/grant-announcement-may-2026/`

Inside the folder:

1. **Write or paste the content** into a file named `content.docx` (or
   `.md`, `.txt`, `.pdf` — any of these work). Include:
   - What happened / what you want to announce
   - Names of people involved (with correct spelling — the skill will ask
     if it's uncertain)
   - Dates, numbers, citations
   - Any quotes (with attribution)

2. **Add photos** to an `images/` subfolder (strongly recommended). JPEG
   or PNG. Use full-resolution originals if you have them.

3. **(Optional) Style reference**: if you want the post to match a particular
   tone or visual direction, add a `style_reference.txt` with a URL, or
   drop in a `.pdf` of the reference document.

Your folder should look like:

```
grant-announcement-may-2026/
├── content.docx
├── images/
│   ├── ceremony.jpg
│   └── recipients_group.jpg
└── style_reference.txt    (optional)
```

### Step 2: Run the skill

In Codex App:

1. Click **+ New chat** in the left sidebar
2. Click **Project** below the chat input
3. Pick your post folder
4. Type: *"Use the cdhai-social-media-officer-linkedin skill on this folder"*

Codex will:
- Read the content
- Detect what kind of post this is (event recap, grant announcement, etc.)
- Ask you any questions where it's uncertain
- Generate the draft

This takes 1-2 minutes.

### Step 3: Run the reviewer

After the writer skill finishes:

> *"Now run the cdhai-content-reviewer skill on this folder"*

This adds a `review_report.docx` with typo and brand checks.

### Step 4: Review the output

Open your post folder. You'll see four new things:

| File | What it is |
|---|---|
| `linkedin_post.docx` | The draft — your main deliverable |
| `report.docx` | Posting instructions, image ranking, items to verify |
| `review_report.docx` | Reviewer findings (typos, brand, hype check) |
| `images_used/` | Top 10 ranked image candidates |

**Open `report.docx` first.** Its "Ready to publish" section tells you
exactly what to do next.

**Open `review_report.docx` second.** Address all CRITICAL items before
posting. Verify all WARNINGS. Apply SUGGESTIONS if you agree.

**Then open `linkedin_post.docx`** and copy the post text.

### Step 5: Post on LinkedIn

1. Go to LinkedIn → click "Start a post"
2. Paste the text from `linkedin_post.docx`
3. Click the photo icon → upload 1-3 images from `images_used/`
   (the report tells you which ones rank highest)
4. Review one more time on LinkedIn (the platform may strip some formatting)
5. Click **Post**

Done.

---

## Common situations

### "Codex asked me a question — what should I do?"

The skill stops and asks when it's uncertain about something that would
embarrass CDHAI if wrong. Examples:

> "I see 'Dr. Yang' in the content but no first name. Is this Andrew Yang
> (the keynote speaker) or someone else? Or should I use 'Dr. Yang' as-is?"

Just type the answer in chat. The skill applies it and continues.

If you don't know the answer, type "skip — flag in report". The skill
will leave a placeholder and note it for human verification later.

### "I don't agree with how the skill wrote the hook"

Tell it in chat:

> "The hook is too academic. Try something more energetic."

The skill rewrites. Then it asks:

> "Should I save this preference? (a) just this run, (b) save as a rule
> for future posts, (c) discard"

Pick:
- **(a) just this run** — for one-off corrections
- **(b) save as a rule** — for patterns you want consistently
- **(c) discard** — if you change your mind

### "There are no photos for this post"

The skill will ask:

> "I don't see any images. Pick one: (a) search Unsplash, (b) generate
> via DALL-E (will be flagged as AI), or (c) proceed text-only."

If you pick (a) or (b), the skill shows candidates and you pick which to
use. If you pick (c), the post goes out text-only (which is fine but
LinkedIn engagement is ~2-3x higher with images).

### "The reviewer flagged something I disagree with"

Two options:

1. **Ignore it** — flags are not edits. The draft stays as-is. The reviewer
   just told you what it noticed.
2. **Tell the reviewer to stop flagging this pattern** — in chat:
   > "Stop flagging the hype density check for grant celebrations"
   The reviewer asks: save as rule? Pick yes to remember the preference.

### "I want to make a small edit to the draft"

Just edit `linkedin_post.docx` in Word. The skill doesn't track edits
made directly to the file — what you save is what gets posted.

If you want the skill to remember the edit for future posts, tell it
in chat what you changed and pick "save as rule".

---

## Where to ask for help

- **Bugs / typos in the skill itself**: open an issue at
  [the GitHub repo](https://github.com/wgu12345/cdhai-social-media-officer-linkedin.skill/issues)
- **Brand questions** (is "CHITA" or "CHEETAH" the current name?):
  ask Wenying or check `_rules/brand_rules.md` in the repo
- **Compliance questions** (can I post about this partner?):
  ask Gordon or partnership office before posting
- **LinkedIn account access**: ask Upasana Sagar (CDHAI program coordinator)

---

## What this skill won't do for you

To set expectations:

- It won't post to LinkedIn for you. (Policy decision — human review required.)
- It won't write content from nothing. You need to provide the source
  material (content.docx).
- It won't fact-check claims against the internet. It flags things to
  verify, but you check the sources.
- It won't write Chinese, Spanish, or any non-English post (v0.3 limitation).
- It won't write for other platforms — Twitter / Instagram / website are
  separate skills.

---

## Roadmap

Wenying is the maintainer. Features coming in later versions:

- **v0.4**: native PowerPoint deck parsing (currently you have to export
  to PDF first); periodic refresh of the peer-institution voice corpus
- **v0.5**: skills for Twitter, Instagram, and the JHU Carey website
- **Later**: Chinese-language support; integration with scheduling tools
  if CDHAI policy allows
