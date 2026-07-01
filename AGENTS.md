# wikiR Agent Contract

wikiR is an Obsidian-compatible vault structure and agent operating protocol. It does not provide or require a custom Python harness. Use the agent runtime's native file reading, search, OCR, and writing capabilities.

## Hard Rules

1. Work locally by default. Do not upload, sync, or call network services unless the user explicitly asks.
2. Treat raw materials as append-only evidence. Do not delete, overwrite, or move files in `00_Inbox/materials/` without explicit user approval.
3. In the public template repository, never commit real private materials, private attachments, secrets, generated scratch files, or local Obsidian workspace state.
4. Use flat Obsidian YAML properties. Avoid nested frontmatter; keep properties short and machine-readable.
5. Users should interact in natural language. Do not ask users to run maintenance commands for normal wiki work.
6. Use Hermes or the current agent runtime's native tools to read files, search the vault, convert documents, and perform OCR when needed.
7. Ground writing in retrieved notes, source cards, and raw materials. If evidence is missing or extraction fails, say so clearly and list the gap.
8. Keep notes concise. Promote only stable, reusable ideas into `02_Notes/`; keep project-specific drafts in `03_Projects/` or `04_Outputs/`.

## Vault Areas

- `00_Inbox/materials/`: new raw materials waiting for agent curation.
- `01_Sources/`: source cards generated from raw materials.
- `02_Notes/`: durable atomic notes and reusable knowledge.
- `03_Projects/`: active project workspaces.
- `04_Outputs/`: generated reports, applications, proposals, and polished drafts.
- `80_Attachments/`: images, PDFs, and other Obsidian attachments.
- `90_System/`: prompts, templates, and agent-facing system guidance.

## Workflows

### New Material

1. User places files in `00_Inbox/materials/`.
2. Agent reads the material with native runtime capabilities.
3. Agent creates or updates source cards in `01_Sources/` using `90_System/templates/source-note.md`.
4. Agent uses `90_System/prompts/curator.md` to fill summary, core points, reusable fragments, links, and next actions.
5. If a concept is reusable across projects, create or update a note in `02_Notes/` with links back to the source card.

### Search and Reuse

1. Agent searches `01_Sources/`, `02_Notes/`, `03_Projects/`, `04_Outputs/`, and relevant raw materials.
2. Agent reads the strongest matching materials directly.
3. Agent drafts the answer or output with citations to source cards and notes.
4. If search or extraction is incomplete, state the limitation before writing.
5. Store substantial deliverables in `04_Outputs/`.

### Quality Gate

Before large reorganizations, public commits, or important outputs, the agent should inspect:

- broken or stale wikilinks;
- missing required YAML properties;
- source cards without `source_path` or usable excerpts;
- outputs that make unsupported claims;
- private materials accidentally staged for public release.

## Prompt Profiles

- Curate new material: `90_System/prompts/curator.md`
- Retrieve and write grounded output: `90_System/prompts/retrieval-writer.md`
- Evaluate retrieval and answer quality: `90_System/prompts/evaluator.md`
