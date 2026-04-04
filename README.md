# TTRPG Weekly Intelligence — Free Version

Fully automated publishing pipeline. **Zero cost. No API keys.**

You generate the report in Claude.ai. You drop the HTML file into GitHub.
Everything else — publishing, archive, index — happens automatically.

---

## How it works

```
You (in Claude.ai)          GitHub                        Live site
──────────────────          ──────                        ─────────
Generate dashboard    →     Drop HTML into /reports   →   Page publishes
(this conversation)         (drag & drop, 30 seconds)     Index auto-rebuilds
```

That's it. One file drop per week. No terminal. No code. No cost.

---

## One-time setup (~10 minutes)

### Step 1 — Create the GitHub repository

1. Go to [github.com](https://github.com) → sign in (or create a free account)
2. Click **+** (top right) → **New repository**
3. Name: `ttrpg-weekly`
4. Visibility: **Public** ← required for free GitHub Pages
5. Click **Create repository**
6. On the next screen click **uploading an existing file**
7. Drag everything from this zip into the window
8. Scroll down → click **Commit changes**

### Step 2 — Enable GitHub Pages

1. In your repo → **Settings** → **Pages** (left sidebar)
2. Source: **Deploy from a branch**
3. Branch: `main` · Folder: `/ (root)`
4. Click **Save**

Your site is now live at:
**`https://YOUR-USERNAME.github.io/ttrpg-weekly`**

(Takes 1–2 minutes. Bookmark this URL — it never changes.)

### Step 3 — Give the Action permission to write

1. In your repo → **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Click **Save**

Setup complete. Nothing else to configure. No API keys. No secrets.

---

## Your weekly workflow (2 minutes)

### In Claude.ai — generate the report

Start a new message (or continue this conversation) with:

```
Generate this week's TTRPG dashboard as a self-contained HTML file.
Use the same format as previous issues. Week of [today's date]. Issue #[N].
Return only the raw HTML — no explanation, no markdown fences.
```

Claude will return a block of HTML.

### Save the HTML

1. Select all the HTML Claude returns (Ctrl+A inside the response)
2. Paste it into a text editor (Notepad, TextEdit, VS Code — anything)
3. Save the file as: **`YYYY-MM-DD.html`** (e.g. `2026-04-11.html`)

### Upload to GitHub

1. Go to your GitHub repo → click the **reports** folder
2. Click **Add file** → **Upload files**
3. Drag your `2026-04-11.html` file into the window
4. Click **Commit changes**

### That's it — GitHub does the rest

Within 60 seconds the Action runs automatically:
- Your new report is live at `.../reports/2026-04-11.html`
- The archive homepage rebuilds with a card for the new issue
- The previous issue is preserved and linked

---

## File naming convention

Reports must be named by date: `YYYY-MM-DD.html`

| Week of       | Filename            |
|---------------|---------------------|
| April 4, 2026 | `2026-04-04.html`   |
| April 11      | `2026-04-11.html`   |
| April 18      | `2026-04-18.html`   |

The archive sorts by filename — newest first.

---

## File structure

```
ttrpg-weekly/
├── .github/
│   └── workflows/
│       └── publish.yml         ← watches /reports, rebuilds index on push
├── reports/
│   └── 2026-04-04.html         ← drop your weekly HTML files here
├── scripts/
│   └── build_index.py          ← rebuilds index.html automatically
├── index.html                  ← archive homepage (auto-rebuilt, don't edit)
└── .gitignore
```

---

## Cost

| Component      | Cost     |
|----------------|----------|
| GitHub repo    | Free     |
| GitHub Pages   | Free     |
| GitHub Actions | Free     |
| Claude.ai      | Free tier or existing subscription |
| **Total**      | **$0**   |

---

## Tips

**Sharing a specific issue**
Each report has a permanent URL: `https://YOUR-USERNAME.github.io/ttrpg-weekly/reports/2026-04-04.html`
Safe to share in newsletters, Slack, Discord — it never moves.

**Keeping issue numbers consistent**
In your Claude.ai prompt, track the issue number manually:
`Issue #2`, `Issue #3`, etc. Or ask Claude to infer it from the date.

**Editing a published report**
Re-upload a corrected HTML file with the same filename — it overwrites the old one and
GitHub Pages serves the new version within a minute.

**Making it private**
GitHub Pages requires a public repo on the free plan. If you want a private archive,
upgrade to GitHub Pro ($4/month) and you can set the repo to private.
