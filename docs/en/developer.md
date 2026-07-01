# wikiR Developer Guide

[简体中文](../zh/developer.md) | [README](../../README.md)

This guide is for maintainers of the wikiR template. wikiR is intentionally a vault protocol and documentation project, not a custom Python harness.

## Repository Strategy

Use two repositories:

- Public template repository: folder structure, agent contract, prompts, templates, examples, and documentation.
- Private vault repository: real source cards, notes, project outputs, and optionally raw materials.

The public repository should not contain private materials, private attachments, generated scratch files, logs, secrets, or local Obsidian workspace state.

## Create a Private Vault

After pushing the public template, create a private working vault:

```sh
cd /path/to/workspace
git clone <PUBLIC_WIKIR_REPO_URL> my-wikiR
cd my-wikiR
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git push -u origin main
```

Open `my-wikiR` in Obsidian and use it as the Hermes working directory.

## Pull Template Updates Into a Private Vault

```sh
cd /path/to/my-wikiR
git fetch upstream
git merge upstream/main
```

After merging, ask Hermes or your local agent to inspect the vault for broken links, missing frontmatter, and unsupported claims.

## Hermes Project Prompt

Use this as a project-level instruction when configuring Hermes:

```text
You are maintaining a wikiR vault. wikiR does not provide a custom harness; use your native local file reading, search, OCR, and writing capabilities.

The working directory is the vault root. First read AGENTS.md and 90_System/prompts/.

When processing new materials, read files from 00_Inbox/materials, create source cards in 01_Sources, and promote durable knowledge to 02_Notes when useful.

For material lookup questions, search 01_Sources, 02_Notes, 03_Projects, 04_Outputs, and relevant raw materials.

For proposals, plans, reports, summaries, and other reuse-heavy writing tasks, gather evidence first, then draft from the evidence. Cite source cards or notes where practical.

After important edits, inspect broken links, YAML properties, source paths, unsupported claims, and accidental staging of private materials.

Do not upload files, do not delete raw materials, and do not invent facts that were not retrieved or otherwise provided.
```

## Document Extraction Policy

Document extraction is a runtime responsibility.

Hermes or the chosen local runtime should handle:

- Word files, including legacy `.doc`;
- PDFs, including scanned PDFs through OCR when available;
- spreadsheets and presentations;
- images and attachments;
- raw text and Markdown.

If extraction fails, the agent should report the failure, keep the raw file untouched, and ask for a converted or OCRed file when needed.

## Public Push Safety Checklist

Before committing to the public repository:

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
git add -n .
```

Only template files, prompts, docs, and safe examples should be staged.

## Private Raw Material Options

In a private vault, choose one:

- Keep default ignores and track only curated Markdown.
- Force-add selected private files with `git add -f`.
- Track raw materials with Git LFS if storage and privacy requirements allow it.

Do not change the public template defaults just because a private vault needs different material-tracking behavior.
