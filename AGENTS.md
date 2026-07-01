# wikiR Agent Contract

This repository is the local-first wikiR template and harness. It can also be used inside a private personal vault. Keep the system small, inspectable, and Obsidian-compatible.

## Hard Rules

1. Work locally by default. Do not upload, sync, or call network services unless the user explicitly asks.
2. Treat raw materials as append-only evidence. Do not delete, overwrite, or move files in `00_Inbox/materials/` without explicit user approval.
3. In the public template repository, never commit real private materials, generated indexes, generated context, logs, secrets, or local Obsidian workspace state.
4. Use flat Obsidian YAML properties. Avoid nested frontmatter; keep properties short and machine-readable.
5. Before answering reuse-heavy requests, build or refresh the local index and retrieve context:
   - `python3 harness/wiki.py build-index`
   - `python3 harness/wiki.py context "<user request>"`
6. Ground writing in retrieved notes and source cards. If evidence is missing or weak, say so and list the gap.
7. Keep notes concise. Promote only stable, reusable ideas into `02_Notes/`; keep project-specific drafts in `03_Projects/` or `04_Outputs/`.
8. Prefer deterministic harness checks for indexing, retrieval, and evaluation. Use the LLM for summarizing, classifying, connecting, and drafting, not as the only source of truth.

## Vault Areas

- `00_Inbox/materials/`: new raw materials waiting for ingestion.
- `01_Sources/`: source cards generated from raw materials.
- `02_Notes/`: durable atomic notes and reusable knowledge.
- `03_Projects/`: active project workspaces.
- `04_Outputs/`: generated reports, applications, proposals, and polished drafts.
- `80_Attachments/`: images, PDFs, and other Obsidian attachments.
- `90_System/`: prompts, templates, indexes, eval cases, and logs.
- `harness/`: local scripts that agents should call.

## Workflows

### New Material

1. User places files in `00_Inbox/materials/`.
2. Run `python3 harness/wiki.py ingest`.
3. Open the generated source card in `01_Sources/`.
4. Use `90_System/prompts/curator.md` to fill summary, core points, reusable fragments, links, and next actions.
5. If a concept is reusable, create or update a note in `02_Notes/` with links back to the source card.

### Search and Reuse

1. Run `python3 harness/wiki.py build-index`.
2. Run `python3 harness/wiki.py context "<task or question>"`.
3. Read `90_System/context/last_context.md`.
4. Draft the answer or output with citations to source cards and notes.
5. Store substantial deliverables in `04_Outputs/`.

### Quality Gate

Run these before large reorganizations or important writing:

```sh
python3 harness/wiki.py doctor
python3 harness/wiki.py eval
```

## Prompt Profiles

- Curate new material: `90_System/prompts/curator.md`
- Retrieve and write grounded output: `90_System/prompts/retrieval-writer.md`
- Evaluate retrieval and answer quality: `90_System/prompts/evaluator.md`
