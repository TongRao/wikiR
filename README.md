# wikiR

[简体中文](docs/zh/README.md) | [Developer guide](docs/en/developer.md)

wikiR is a local-first template for building an agent-maintained personal knowledge vault. It is designed for Obsidian, Hermes-style local agents, and local LLM workflows.

The project provides a vault structure, an agent contract, prompt profiles, and note templates so your materials can be curated, searched, and reused without relying on a cloud knowledge base or a custom Python toolchain.

## Why wikiR

- Local first: raw materials and notes stay in your vault by default.
- Agent maintained: users work in natural language while the local agent reads, searches, and writes in the background.
- Obsidian compatible: notes are plain Markdown with flat YAML properties and wikilinks.
- Evidence oriented: raw materials become traceable source cards before they are reused.
- Runtime agnostic: Hermes or another local agent can use its own file readers, OCR, search, and document tools.
- Human maintainable: the system is mostly folders, prompts, templates, and conventions.

## How It Works

```text
raw materials
  -> source cards
  -> durable notes
  -> project workspaces
  -> grounded drafts and outputs
```

Users should not need to run maintenance commands manually. A local agent reads `AGENTS.md`, follows the prompts and templates in `90_System/`, and writes curated notes or outputs back into the vault.

## Core Layout

- `00_Inbox/materials/`: raw material inbox.
- `01_Sources/`: source cards generated from raw materials.
- `02_Notes/`: durable notes and reusable knowledge.
- `03_Projects/`: active project workspaces.
- `04_Outputs/`: drafts, proposals, reports, and other deliverables.
- `80_Attachments/`: Obsidian attachments.
- `90_System/`: prompts, templates, and agent-facing system guidance.

## Typical Use

1. Create a private vault from this template.
2. Open the private vault in Obsidian.
3. Set Hermes or another local agent to use the vault as its working directory.
4. Add new materials to `00_Inbox/materials/`.
5. Ask the agent to curate materials, find reusable evidence, or draft an output.

Example requests:

- "I added new materials. Please curate them."
- "Find reusable materials related to this project."
- "Draft a proposal from the existing vault materials."
- "Check whether this vault has broken links or unsupported claims."

## Documentation

- [Architecture](docs/en/architecture.md)
- [Agent operating protocol](docs/en/agent-runtime.md)
- [Open-source template and private vault workflow](docs/en/open-source-template-and-private-vault.md)
- [Developer guide](docs/en/developer.md)

## Safety Defaults

The default `.gitignore` excludes raw materials, attachments, logs, secrets, and local Obsidian workspace state. This keeps the public template safe by default.

For real personal use, maintain this repository as a public template and keep your actual vault in a separate private repository.
