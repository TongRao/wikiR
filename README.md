# wikiR

wikiR is a local material-management workspace for Hermes Agent, document parsing, material archiving, wiki generation, and Obsidian-based review.

The project does not require Obsidian to open the whole repository. Obsidian should open only the `wiki/` directory.

## What It Does

1. Users drop raw files into `00_inbox/`.
2. Hermes calls the project MCP server when the user says "process inbox" or "处理文件".
3. The MCP tools parse supported files into Markdown, metadata JSON, CSV tables, and reports.
4. Raw files are archived under `01_raw_archive/`.
5. Hermes uses parsed outputs to create material indexes, wiki candidates, reusable passages, and project drafts.

## Directory Layout

```text
.
├── 00_inbox/
├── 01_raw_archive/
│   └── YYYY/
├── 02_parsed/
│   └── YYYY/
├── 03_materials/
├── wiki/
│   ├── 00_home.md
│   ├── 01_wiki/
│   │   ├── ai_tech/
│   │   ├── power_grid/
│   │   ├── writing_methods/
│   │   └── _pending/
│   ├── 02_projects/
│   ├── 03_reusable/
│   │   ├── _pending/
│   │   ├── technical_routes/
│   │   ├── result_indicators/
│   │   └── common_phrases/
│   ├── 04_templates/
│   ├── 05_index/
│   └── 99_attachments/
├── 05_drafts/
├── 06_logs/
├── 07_config/
├── 08_MCP/
└── scripts/
```

## Install Dependencies

Create a virtual environment, then install the MCP server dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r 08_MCP/requirements.txt
```

`08_MCP/requirements.txt` includes:

- `mcp`: MCP server runtime.
- `markitdown[docx,pdf,pptx]`: required for `.docx`, `.pdf`, `.pptx`, and other common document-to-Markdown conversion.
- `openpyxl`: required for `.xlsx` / `.xlsm` sheet extraction.
- `python-docx`: reserved as a Word fallback dependency.

Verify the key packages after installation:

```sh
.venv/bin/python -c "import mcp, markitdown, openpyxl; print('dependencies ok')"
```

If you previously installed plain `markitdown` and PDF/DOCX conversion fails with a missing optional dependency error, reinstall:

```sh
.venv/bin/pip install -U "markitdown[docx,pdf,pptx]"
```

The first version uses MarkItDown for common document conversion and OpenPyXL for Excel extraction. OCR-heavy workflows should be added later as an explicit extension.

## Initialize Workspace

```sh
python scripts/init_workspace.py
```

This creates the required folders and base files without overwriting existing files.

## Start MCP Server

```sh
bash scripts/start_mcp.sh
```

The script starts `08_MCP/material_mcp_server.py` with stdio transport. If `.venv/` does not exist, it prints setup instructions and exits. It does not install dependencies automatically.

When the MCP server starts successfully, the script prints a short status message to stderr, then waits for Hermes MCP messages over stdio. Seeing no further output after the startup message is normal.

## Process Inbox Manually

Hermes should normally call the MCP tool. This command is only for local smoke tests:

```sh
python scripts/process_inbox_cli.py --mode fast
```

Supported first-version formats:

- `.docx`
- `.pdf`
- `.xlsx`
- `.xlsm`
- `.pptx`
- `.txt`
- `.md`

## Naming Rules

Successful parsing uses the same canonical name for parsed folders, archived originals, and source copies:

```text
类别_YYYYMMDD_文件名_hash
```

Examples:

- `政策_20260701_2027年工业领域科技计划项目申报指南_d6108b84`
- `申报书_20260701_重点研发计划项目申报书_1a2b3c4d`

The parser keeps the useful part of the original filename, removes leading attachment markers such as `附件3：`, and classifies the material with lightweight local rules. Current built-in categories include `政策`, `报奖`, `申报书`, `合同`, `表格`, and fallback `材料`.

Parsed outputs are grouped by year under `02_parsed/YYYY/`. Archived originals are grouped by year under `01_raw_archive/YYYY/`.

## Connect Hermes

Configure Hermes to start the MCP server with:

```sh
bash scripts/start_mcp.sh
```

When the user says "process inbox" or "处理文件", Hermes should call `process_inbox`. For individual files, it can call `convert_document` or `extract_excel_workbook`.

## Obsidian

Open only:

```text
wiki/
```

Generated wiki candidates are written to `wiki/01_wiki/_pending/` for review before being moved into final wiki folders.

## Safety Boundaries

- All tool reads and writes are restricted to the project root.
- Tools must not access `~/.ssh`, `~/.gnupg`, browser profiles, system keychains, or any path outside this repository.
- Raw files are never deleted as the only copy.
- Parsed outputs and archive movement happen only after conversion succeeds.
- If conversion fails, the original file remains in `00_inbox/` and a concise failure log is written under `06_logs/`.
- Existing files under `01_raw_archive/` are not overwritten; name conflicts get a timestamp/hash suffix.
- MCP responses are concise JSON and do not return long document bodies.
- Failures generate a concise log under `06_logs/` instead of failing silently.
