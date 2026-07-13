# wikiR MCP Server

This directory contains the MCP server used by Hermes to process local materials.

## Tools

- `health_check()`
- `init_workspace(overwrite=False)`
- `process_inbox(mode="fast")`
- `convert_document(source_path, mode="fast")`
- `extract_excel_workbook(source_path)`
- `create_material_index(parsed_dir=None)`
- `generate_wiki_candidates(parsed_item_path=None)`
- `get_workspace_summary()`

## Setup

From the project root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r 08_MCP/requirements.txt
```

## Start

```sh
bash scripts/start_mcp.sh
```

The server uses stdio transport.

## Parse Naming

Successful conversions use `类别_YYYYMMDD_文件名_hash`. Parsed items are written under `02_parsed/YYYY/`, and archived originals under `01_raw_archive/YYYY/`. Failed conversions do not create parsed items or archive the source file; they leave the source in `00_inbox/` and write a short log under `06_logs/`.

## Safety

All tool paths are resolved against the project root. Paths outside the workspace are rejected.
