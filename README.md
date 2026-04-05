# The Dungeon Economy

A free, automated publishing pipeline for a weekly D&D intelligence brief.

You generate the report in Claude.ai using a two-prompt workflow.
You drop the HTML file into GitHub.
Everything else — publishing, archive, index — happens automatically.

**Cost: $0. No API keys. No servers. No code to run.**

---

## How it works

```
Claude.ai (Prompt 1)       Claude.ai (Prompt 2)        GitHub                   Live site
────────────────────       ────────────────────         ──────                   ─────────
Research report       →    Render to HTML           →   Drop into /reports   →   Publishes instantly
(markdown output)          (self-contained file)        (drag & drop)            Index auto-rebuilds
```

Two conversations. One file drop. Live in under five minutes.

---

## One-time setup (~10 minutes)

### Step 1 — Create the GitHub repository

1. Go to [github.com](https://github.com) → sign in (or create a free account)
2. Click **+** (top right) → **New repository**
3. Name: `dungeon-economy` (or any name you prefer)
4. Visibility: **Public** ← required for free GitHub Pages
5. Click **Create repository**
6. Click **uploading an existing file**
7. Drag everything from this folder into the upload window
8. Click **Commit changes**

### Step 2 — Enable GitHub Pages

1. In your repo → **Settings** → **Pages** (left sidebar)
2. Source: **Deploy from a branch**
3. Branch: `main` · Folder: `/ (root)`
4. Click **Save**

Your site will be live at:
**`https://YOUR-USERNAME.github.io/dungeon-economy`**

(Takes 1–2 minutes the first time. Bookmark it — the URL never changes.)

### Step 3 — Give the Action write permission

1. In your repo → **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Click **Save**

Setup complete. Nothing else to configure.

---

## Your weekly workflow (~5 minutes)

### Step 1 — Run the research prompt (Prompt 1)

In Claude.ai, start a conversation and paste **Prompt 1** (the research and
intelligence prompt). Claude will return a structured markdown report covering:

- Executive Read
- This Week's Verified Developments
- Market and Commercial Movement
- Community Sentiment
- Observations and Interpretation
- Implications by Audience
- What to Watch Next
- Source Ledger
- Method Note

Copy the full markdown output.

### Step 2 — Run the HTML prompt (Prompt 2)

In a new Claude.ai conversation, paste **Prompt 2** (the HTML rendering prompt).
Replace the `[PASTE FULL PROMPT 1 OUTPUT HERE]` placeholder with the markdown
from Step 1. Claude will return a complete, self-contained HTML file.

### Step 3 — Save the HTML

1. Select all the HTML Claude returns
2. Paste into a text editor (Notepad, TextEdit, VS Code — anything)
3. Save the file as: **`YYYY-MM-DD.html`** using the Friday publication date

   Examples: `2026-04-11.html` · `2026-04-18.html` · `2026-04-25.html`

### Step 4 — Upload to GitHub

1. Go to your repo on github.com
2. Click the **reports** folder
3. Click **Add file** → **Upload files**
4. Drag your `YYYY-MM-DD.html` file into the window
5. Click **Commit changes**

### Done — GitHub does the rest automatically

Within 60 seconds:
- Your new issue is live at `.../reports/YYYY-MM-DD.html`
- The archive homepage rebuilds with a card for the new issue
- All previous issues remain live at their permanent URLs

---

## File naming convention

Reports must follow the `YYYY-MM-DD.html` date format. The archive sorts by
filename — newest first.

| Publication date | Filename            |
|------------------|---------------------|
| April 11, 2026   | `2026-04-11.html`   |
| April 18, 2026   | `2026-04-18.html`   |
| April 25, 2026   | `2026-04-25.html`   |

---

## File structure

```
dungeon-economy/
├── .github/
│   └── workflows/
│       └── publish.yml         ← triggers on new /reports files, rebuilds index
├── reports/
│   └── 2026-04-05.html         ← drop weekly HTML files here
├── scripts/
│   └── build_index.py          ← generates index.html in the publication design
├── index.html                  ← archive homepage (auto-rebuilt — do not edit)
└── .gitignore
```

---

## How the index rebuilds

When you push a new HTML file to `/reports`, the GitHub Action runs
`scripts/build_index.py` automatically. The script:

1. Scans all `*.html` files in `/reports`, sorted newest first
2. Extracts the issue number, headline, and preview text from each file
3. Generates a new `index.html` in The Dungeon Economy design — dark mode
   default, light mode toggle, matching the issue design system exactly
4. Commits the updated index back to the repo

The "Latest" badge automatically moves to whichever issue is newest.

---

## Cost

| Component        | Cost                               |
|------------------|------------------------------------|
| GitHub repo      | Free                               |
| GitHub Pages     | Free                               |
| GitHub Actions   | Free (well within free tier limits)|
| Claude.ai        | Free tier or existing subscription |
| **Total**        | **$0**                             |

---

## Tips

**Sharing a specific issue**
Each issue has a permanent URL:
`https://YOUR-USERNAME.github.io/dungeon-economy/reports/2026-04-11.html`
Safe to share in newsletters, Discord, or Slack — it never changes.

**Tracking issue numbers**
Include the issue number in your Prompt 1 and Prompt 2 instructions, e.g.
`Issue #2`, `Issue #3`. The archive index reads the number directly from the HTML.

**Correcting a published issue**
Re-upload a corrected file with the same filename — it overwrites the old one.
GitHub Pages serves the corrected version within about a minute.

**Changing the publication name**
The design, branding, and footer text are all embedded inside each HTML file
generated by Prompt 2. Update Prompt 2's `PUBLICATION IDENTITY` section to
change the name, tagline, and footer line before generating new issues.

**Making the archive private**
GitHub Pages requires a public repo on the free plan. To make the archive
private, upgrade to GitHub Pro ($4/month) and set the repo to private.
