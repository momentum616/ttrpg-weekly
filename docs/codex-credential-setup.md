# Codex Credential Setup

This repository is a static GitHub Pages publication pipeline. It currently has
no runtime API credentials: reports are committed as HTML, and GitHub Actions
uses the repository-provided `GITHUB_TOKEN` to rebuild and commit `index.html`.

## Account Roles

- `momentum616`: owns `momentum616/ttrpg-weekly` and GitHub Pages publishing.
- `mmtm-studios`: connected to Codex/GitHub app and should have write access
  for Codex-assisted updates.

## Local Git Identity

Use repository-local Git identity settings so commits in this checkout are
attributed to the publishing account without changing other projects:

```powershell
git config user.name "momentum616"
git config user.email "273568026+momentum616@users.noreply.github.com"
```

This affects commit metadata only. Push permission is controlled separately by
the credential used by Git or GitHub CLI.

## Recommended Two-Account Git Setup

Use separate SSH keys and host aliases so each repository can point at the
correct GitHub account without repeatedly switching global credentials:

```sshconfig
Host github-momentum616
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_momentum616
  IdentitiesOnly yes

Host github-mmtm-studios
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_mmtm_studios
  IdentitiesOnly yes
```

Then set this repository's remote to the publishing account alias:

```powershell
git remote set-url origin git@github-momentum616:momentum616/ttrpg-weekly.git
```

Keep any `mmtm-studios` remotes or repositories pointed at the studio alias.

## GitHub CLI

The local `gh` profile should be authenticated separately from Git SSH if you
want Codex to open pull requests or inspect private resources through the CLI:

```powershell
gh auth login -h github.com
gh auth status
```

The local `gh` profile is authenticated as `mmtm-studios` with `repo` and
`workflow` scopes. `mmtm-studios` has write permission on
`momentum616/ttrpg-weekly`, so Codex can use this account to push branches and
open pull requests while `momentum616` remains the repository owner.

## Secrets

Do not commit secrets. If the project later adds automated research, LLM calls,
email, newsletter publishing, or private APIs:

- add safe placeholders to `.env.example`
- keep real local values in `.env`
- put production values in GitHub Actions secrets
- document which account owns each secret
