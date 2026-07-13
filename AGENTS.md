# wikiR Agent Guide

wikiR is a local material-management workspace for document parsing, material archiving, wiki generation, and Obsidian use. Hermes should work inside this project root and use the project MCP server for file processing.

## Hard Rules

1. Stay inside the current project root. Do not access files outside this workspace.
2. Do not read sensitive user locations such as `~/.ssh`, `~/.gnupg`, browser profiles, system keychains, or any path outside the project root.
3. Do not directly process raw `docx`, `pdf`, `xlsx`, `pptx`, or similar originals in long-form reasoning. When the user says "process inbox" or "处理文件", call the MCP tool first.
4. Original files must be archived. Never delete the only copy of a raw file.
5. Use Markdown, CSV, and JSON under `02_parsed/` as the main working versions after processing.
6. Obsidian should open `wiki/`, not the project root.
7. Wiki candidate pages must first be written to `wiki/01_wiki/_pending/`.
8. Do not run `git commit`, `git push`, or dependency installation unless the user explicitly asks.
9. Keep responses formal, pragmatic, and suitable for project-material writing.

## Normal Workflow

1. User puts new files into `00_inbox/`.
2. User asks Hermes to "process inbox" or "处理文件".
3. Hermes calls the MCP server tool `process_inbox`.
4. The MCP tool archives raw files under `01_raw_archive/YYYY/` and writes parsed Markdown/CSV/JSON/report files under `02_parsed/YYYY/`.
5. Hermes uses parsed outputs to create or update material indexes, wiki candidate pages, reusable passages, and project drafts.

Successful parse names follow:

```text
类别_YYYYMMDD_文件名_hash
```

The MCP tools preserve the meaningful original filename, remove leading attachment labels such as `附件3：`, classify the material with local rules and converted-text hints, and use the same canonical name for the parsed folder, archived original, and parsed source copy. If conversion fails, no parsed item or archive copy should be created; the original remains in `00_inbox/`, and a failure log is written under `06_logs/`.

## Important Locations

- `00_inbox/`: user drop zone for new raw files.
- `01_raw_archive/`: archived originals.
- `02_parsed/`: parsed Markdown, metadata, tables, images, and processing reports.
- `03_materials/`: generated material indexes.
- `wiki/`: Obsidian vault.
- `05_drafts/`: draft outputs.
- `06_logs/`: local logs.
- `07_config/`: local configuration.
- `08_MCP/`: MCP server and tool implementation.
