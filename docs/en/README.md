# wikiR Documentation

wikiR is a local-first open-source template for a personal wiki and document reuse vault. It is designed for Obsidian, Hermes, local Qwen 35B MoE, and similar local agent workflows.

It is not a cloud knowledge base, and it does not require uploading your materials to online services. It provides a reusable local vault structure, an agent contract, prompt templates, and an inspectable retrieval harness.

## Use Cases

- Manage a durable personal knowledge base with Obsidian.
- Turn PDFs, Word files, spreadsheets, and Markdown documents into traceable source cards.
- Let a local agent draft proposals, plans, reports, and project documents from existing materials.
- Use a small harness to control indexing, retrieval, context generation, and evaluation instead of relying only on an LLM black box.

## Recommended Repository Model

Use two repositories:

- Public repository: maintains the wikiR template, harness, prompts, templates, examples, and documentation.
- Private repository: stores your real personal vault, source cards, notes, project outputs, and optionally raw materials.

For the full workflow, see: [Open Source Template + Private Vault Workflow](open-source-template-and-private-vault.md).

## Quick Start

If you only maintain the open-source template:

```sh
git clone <PUBLIC_WIKIR_REPO_URL> wikiR
cd wikiR
```

If you want to create a real private vault:

```sh
cd /path/to/workspace
git clone <PUBLIC_WIKIR_REPO_URL> wikiR-private
cd wikiR-private
git remote rename origin upstream
git remote add origin <PRIVATE_WIKIR_VAULT_REPO_URL>
git push -u origin main
```

Then open `wikiR-private` in Obsidian and use it as the Hermes working directory.

## Agent Tool Workflow

The normal wikiR workflow should not require users to open a terminal and run commands. Hermes or another local agent runtime should call tools automatically.

Tool definitions live in `harness/tool_manifest.json`, and the low-level adapter is `harness/wiki_tool.py`. Users should make natural-language requests:

- "I added new materials. Please curate them."
- "Find reusable materials related to this project."
- "Draft a proposal from existing materials."
- "Check whether this vault has broken links or index issues."

For details, see: [Agent Runtime Integration](agent-runtime.md).

## Directory Convention

- `00_Inbox/materials/`: entry point for new raw materials. Files are not moved or deleted by default.
- `01_Sources/`: source cards for raw materials, including summaries, key points, excerpts, source paths, and processing status.
- `02_Notes/`: durable atomic notes and reusable knowledge.
- `03_Projects/`: project workspaces for requirements, plans, proposal material, and task context.
- `04_Outputs/`: final drafts, applications, proposals, plans, and reports.
- `80_Attachments/`: Obsidian attachments.
- `90_System/`: prompts, templates, indexes, eval cases, and logs.
- `harness/`: local scripts.

## Hermes / Local Model Integration

Hermes or another local agent runner should follow `AGENTS.md` and bind the wikiR tools:

- Call `wiki_ingest` before curating new materials.
- Call `wiki_build_index` and `wiki_context` before writing.
- Call `wiki_search` for material lookup.
- Call `wiki_doctor` after important changes.
- When retrieval quality degrades, add cases to `90_System/evals/retrieval_cases.jsonl` and call `wiki_eval`.

The current harness is a zero-dependency lexical retrieval baseline. It is intentionally simple and inspectable. Local embeddings or rerankers can be added later without changing the vault structure.

## Obsidian Writing Standard

- Every formal Markdown file should use YAML properties at the top.
- Keep properties flat: `type`, `status`, `created`, `updated`, `tags`, `aliases`, `source_path`, and similar fields.
- Prefer Obsidian wikilinks for internal links.
- Do not place long prose in properties. Use Markdown headings for body content.
- Avoid filenames that contain `# | ^ : %% [[ ]]` or other characters that can break links.

## More Documentation

- [Architecture](architecture.md)
- [Agent Runtime Integration](agent-runtime.md)
- [Open Source Template + Private Vault Workflow](open-source-template-and-private-vault.md)
