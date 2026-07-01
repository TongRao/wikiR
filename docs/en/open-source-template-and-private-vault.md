# Open Source Template + Private Vault Workflow

This repository should be maintained as the open-source wikiR template. It should not be the real private vault.

## Recommended Split

Use two repositories:

- Public repository: `wikiR`
  - Purpose: vault structure, agent contract, prompts, templates, docs, and safe examples.
  - Do not commit real raw materials, private attachments, generated scratch files, logs, or secrets.
- Private repository: your actual personal vault.
  - Purpose: real source cards, notes, project drafts, outputs, and optionally raw materials.
  - Can pull improvements from the public template.

## Public Repository Contents

Track:

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `.gitattributes`
- `.obsidian/app.json`
- `90_System/prompts/`
- `90_System/templates/`
- `docs/`
- Example notes or demo source cards that contain no private data.

Ignore:

- `00_Inbox/materials/`
- `00_Inbox/triage/`
- `80_Attachments/`
- `90_System/logs/`
- `.env*`
- local Obsidian workspace state.

## Create Your Private Vault From This Template

After the public repo is pushed, create a private working vault in another directory:

```sh
cd /Users/tongrao/Desktop/project
git clone <PUBLIC_WIKIR_REPO_URL> my-wikiR
cd my-wikiR
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git branch -M main
git push -u origin main
```

Then use `/Users/tongrao/Desktop/project/my-wikiR` as your Obsidian vault and Hermes working directory.

## Keeping Template Updates

When the public template improves:

```sh
cd /Users/tongrao/Desktop/project/my-wikiR
git fetch upstream
git merge upstream/main
```

After merging, ask Hermes or your local agent to inspect the vault for broken links, missing metadata, and unsupported claims.

## Managing Real Materials In The Private Repo

There are three sane options.

### Option A: Track Curated Markdown Only

Keep the default `.gitignore`.

- Raw files stay local in `00_Inbox/materials/`.
- Source cards, notes, projects, and outputs are committed.
- Best when raw files are large, sensitive, or frequently replaced.

### Option B: Track Selected Raw Materials

Keep the default `.gitignore`, but force-add specific files in the private repo:

```sh
git add -f 00_Inbox/materials/example.pdf
git add -f 80_Attachments/example.png
git commit -m "Add selected private materials"
```

Best when only a few raw files need versioning.

### Option C: Track All Raw Materials Privately

In the private repo only, edit `.gitignore` and remove these blocks:

```gitignore
00_Inbox/materials/*
!00_Inbox/materials/.gitkeep

80_Attachments/*
!80_Attachments/.gitkeep
```

If the private repo will contain PDFs, Word files, audio, video, or large datasets, use Git LFS:

```sh
git lfs install
git lfs track "*.pdf" "*.doc" "*.docx" "*.xls" "*.xlsx" "*.ppt" "*.pptx" "*.mp4" "*.mov" "*.wav" "*.mp3"
git add .gitattributes
git add 00_Inbox/materials 80_Attachments
git commit -m "Track private vault materials"
```

Best when your private remote is reliable and storage limits are acceptable.

## Safety Checks Before Public Push

Run these in the public template repo:

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
```

Only ignored files should include private materials and local artifacts.

Before committing publicly, inspect staged files:

```sh
git add .
git status --short
git diff --cached --stat
git diff --cached --name-only
```

If private files appear, unstage them:

```sh
git restore --staged <path>
```
