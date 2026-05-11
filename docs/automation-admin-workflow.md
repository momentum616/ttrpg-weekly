# Automation and Admin Workflow Plan

## Goal

Automate the weekly research draft while keeping publication gated by a human
approval step.

Desired flow:

1. A scheduled job runs the initial research prompt.
2. The system emails the editor that a draft is ready.
3. The editor reviews the draft in an admin interface.
4. The editor can approve, decline, or generate a new draft.
5. Only final approval publishes a new report to the public site.

## Current Constraint

The current project is a static GitHub Pages site. Static GitHub Pages can host
published reports and a read-only admin UI, but it cannot safely hold private
API keys or perform authenticated publish actions by itself.

Any automated research, email sending, or admin approval action needs a trusted
execution environment such as GitHub Actions, a small serverless backend, or
both.

## Recommended Architecture

### Phase 1: GitHub Actions Draft Pipeline

Use GitHub Actions as the first trusted automation layer.

- Scheduled workflow runs weekly.
- Workflow calls an LLM API with the research prompt.
- Draft output is saved under `drafts/YYYY-MM-DD.md` or `drafts/YYYY-MM-DD.json`.
- Workflow opens or updates a draft pull request.
- Workflow sends an email notification with a link to the draft review page or PR.

Secrets required:

- `LLM_API_KEY`
- `EMAIL_API_KEY`
- `EDITOR_EMAIL`

This keeps generated work out of `main` until reviewed.

### Phase 2: Approval-Gated Publishing

Publishing should happen only after explicit approval.

Possible approval models:

- Merge a generated pull request to publish.
- Use a protected GitHub Actions `workflow_dispatch` approval.
- Use a custom admin page backed by a serverless API.

The simplest safe MVP is pull-request approval:

- Generated draft lives in a PR.
- Editor reviews the generated content.
- Editor requests a regenerated draft by re-running the workflow.
- Editor approves by merging.
- Merge to `main` publishes through the existing GitHub Pages flow.

### Phase 3: Admin Page

For a dedicated admin page with Approve, Decline, and Generate New buttons, add a
small authenticated backend.

Recommended backend options:

- Cloudflare Worker
- Vercel serverless function
- Netlify function

The backend would:

- authenticate the editor
- read draft state from GitHub
- trigger a regenerate workflow
- approve/publish by merging a PR or dispatching a publish workflow
- send status emails

The static admin page can live in this repo, but write actions should go through
the backend so API keys are never exposed in browser JavaScript.

## Draft States

Suggested draft lifecycle:

- `scheduled`: workflow created a draft request
- `drafted`: research output exists
- `needs_review`: email sent, awaiting editor action
- `declined`: editor rejected this draft
- `regenerating`: editor requested a new draft
- `approved`: editor accepted the draft
- `published`: report was merged into `main`

## Repository Shape

Potential future structure:

```text
.github/workflows/
  scheduled-research.yml
  regenerate-draft.yml
  publish-approved-report.yml

admin/
  index.html
  admin.js
  admin.css

drafts/
  YYYY-MM-DD.json

reports/
  YYYY-MM-DD.html

scripts/
  run_research.py
  render_report.py
  send_email.py
  build_index.py
```

## First Build Milestone

Build the smallest safe version first:

1. Add a scheduled GitHub Action.
2. Store the research prompt in the repo.
3. Generate a draft artifact or draft file.
4. Send an email notification.
5. Keep publication manual through PR approval.

After that works reliably, add the custom admin page and backend.

## MVP Implemented On This Branch

The first MVP scaffold lives on `codex/automation-admin-workflow`.

It adds:

- `.github/workflows/scheduled-research.yml`
- `prompts/weekly-research.md`
- `scripts/run_research.py`
- `scripts/send_email.py`
- `drafts/.gitkeep`

The workflow runs on a weekly schedule and can also be triggered manually. It:

1. resolves a publication date
2. runs the weekly research prompt through the OpenAI Responses API with web
   search enabled
3. writes `drafts/YYYY-MM-DD.md` and `drafts/YYYY-MM-DD.json`
4. pushes those draft files to `draft/research-YYYY-MM-DD`
5. opens or updates a draft PR against `main`
6. sends an editor notification email when email secrets are configured

The draft PR is the MVP review surface. Merging is still the human approval
gate, and the workflow does not publish a report directly.

## Required Secrets And Variables

Add these in GitHub under **Settings -> Secrets and variables -> Actions**.

Required secret:

- `OPENAI_API_KEY`: OpenAI API key used by `scripts/run_research.py`

Recommended repository variables:

- `OPENAI_MODEL`: defaults to `gpt-5`
- `OPENAI_REASONING_EFFORT`: defaults to `low`

Email requires one of these provider setups.

For Resend:

- `RESEND_API_KEY`
- `EMAIL_FROM`
- `EDITOR_EMAIL`

For SMTP:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EDITOR_EMAIL`

If no email provider is configured, draft generation still works and the
workflow logs the notification content instead of sending it.

## Testing The MVP

Before merging this workflow into `main`, test it from the dev branch with a
manual workflow dispatch after pushing the branch.

The production weekly schedule only becomes active when the workflow exists on
the default branch.
