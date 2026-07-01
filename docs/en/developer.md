# wikiR Developer Guide

[简体中文](../zh/developer.md) | [README](../../README.md)

This guide is for maintainers and people integrating wikiR with a local agent runtime. The public README is intentionally user-facing; implementation details, private-vault setup, and debugging notes live here.

## Repository Strategy

Use two repositories:

- Public template repository: architecture, harness, prompts, templates, examples, and documentation.
- Private vault repository: real source cards, notes, project outputs, and optionally raw materials.

The public repository should not contain private materials, generated indexes, generated context, logs, secrets, or local Obsidian workspace state.

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

After merging, ask Hermes or your local agent to call `wiki_doctor`.

## Agent Tool Layer

Tool definitions live in:

```text
harness/tool_manifest.json
```

The JSON adapter is:

```text
harness/wiki_tool.py
```

Hermes or another runtime should bind these tools and call them automatically. Users should normally make natural-language requests instead of running terminal commands.

Tool names:

- `wiki_init`
- `wiki_ingest`
- `wiki_build_index`
- `wiki_search`
- `wiki_context`
- `wiki_doctor`
- `wiki_eval`

## Hermes Project Prompt

Use this as a project-level instruction when configuring Hermes:

```text
You are maintaining a wikiR vault. The user should not manually run harness commands; you must call wikiR tools in the background.

The working directory is the vault root. First read AGENTS.md, harness/tool_manifest.json, and 90_System/prompts/.

When processing new materials, call wiki_ingest, then curate the generated source cards in 01_Sources and promote durable knowledge to 02_Notes when useful.

For material lookup questions, call wiki_build_index and then wiki_search.

For proposals, plans, reports, summaries, and other reuse-heavy writing tasks, call wiki_build_index and then wiki_context. Read 90_System/context/last_context.md before drafting.

After important edits, call wiki_doctor. After retrieval logic or eval-case changes, call wiki_eval.

Do not upload files, do not delete raw materials, and do not invent facts that were not retrieved or otherwise provided.
```

## Debug the Tool Layer

The CLI exists as deterministic implementation and debug fallback. It is not the intended daily user interface.

Validate the JSON tool adapter:

```sh
python3 harness/wiki_tool.py '{"tool":"wiki_doctor","args":{}}'
python3 harness/wiki_tool.py '{"tool":"wiki_search","args":{"query":"local knowledge base proposal","top_k":5}}'
python3 harness/wiki_tool.py '{"tool":"wiki_eval","args":{}}'
```

Validate the underlying CLI when needed:

```sh
python3 harness/wiki.py doctor
python3 harness/wiki.py eval
```

## Public Push Safety Checklist

Before committing to the public repository:

```sh
git status --short --ignored
git check-ignore -v 00_Inbox/materials/*
git check-ignore -v 90_System/context/last_context.md
git check-ignore -v 90_System/index/wiki_index.jsonl
git add -n .
```

Only template files, prompts, harness code, docs, and safe examples should be staged.

## Private Raw Material Options

In a private vault, choose one:

- Keep default ignores and track only curated Markdown.
- Force-add selected private files with `git add -f`.
- Track raw materials with Git LFS if storage and privacy requirements allow it.

Do not change the public template defaults just because a private vault needs different material-tracking behavior.
