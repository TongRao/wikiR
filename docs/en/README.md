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
python3 harness/wiki.py doctor
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

## Common Commands

```sh
# Initialize or repair required directories
python3 harness/wiki.py init

# Scan 00_Inbox/materials and create source cards in 01_Sources
python3 harness/wiki.py ingest

# Build the local text index for Sources / Notes / Projects / Outputs
python3 harness/wiki.py build-index

# Search from the command line
python3 harness/wiki.py search "your question or task"

# Generate a context file for the local model
python3 harness/wiki.py context "your question or task"

# Check frontmatter, broken links, and index freshness
python3 harness/wiki.py doctor

# Run retrieval regression tests from 90_System/evals/retrieval_cases.jsonl
python3 harness/wiki.py eval
```

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

Hermes or another local agent runner only needs to follow `AGENTS.md`:

- Call `ingest` before curating new materials.
- Call `build-index` and `context` before writing.
- Call `doctor` after important changes.
- When retrieval quality degrades, add cases to `90_System/evals/retrieval_cases.jsonl` and run `eval`.

The current harness is a zero-dependency lexical retrieval baseline. It is intentionally simple and inspectable. Local embeddings or rerankers can be added later without changing the vault structure.

## Obsidian Writing Standard

- Every formal Markdown file should use YAML properties at the top.
- Keep properties flat: `type`, `status`, `created`, `updated`, `tags`, `aliases`, `source_path`, and similar fields.
- Prefer Obsidian wikilinks for internal links.
- Do not place long prose in properties. Use Markdown headings for body content.
- Avoid filenames that contain `# | ^ : %% [[ ]]` or other characters that can break links.

## More Documentation

- [Architecture](architecture.md)
- [Open Source Template + Private Vault Workflow](open-source-template-and-private-vault.md)
