#!/usr/bin/env python3
"""MCP server exposing wikiR material-processing tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from tools.document_convert import convert_document as convert_document_impl
from tools.inbox_process import process_inbox as process_inbox_impl
from tools.material_index import create_material_index as create_material_index_impl
from tools.paths import PROJECT_ROOT, directory_status, init_workspace_files
from tools.wiki_generate import generate_wiki_candidates as generate_wiki_candidates_impl


mcp = FastMCP("wikiR material MCP")


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return service status and key directory checks."""
    return {
        "status": "ok",
        "workspace_root": str(PROJECT_ROOT.resolve()),
        "directories": directory_status(),
    }


@mcp.tool()
def init_workspace(overwrite: bool = False) -> dict[str, Any]:
    """Create required workspace directories and base files."""
    result = init_workspace_files(overwrite=overwrite)
    return {"status": "ok", **result}


@mcp.tool()
def process_inbox(mode: str = "fast") -> dict[str, Any]:
    """Process all supported files in 00_inbox."""
    return process_inbox_impl(mode=mode)


@mcp.tool()
def convert_document(source_path: str, mode: str = "fast") -> dict[str, Any]:
    """Convert a single supported document inside the project root."""
    return convert_document_impl(source_path=source_path, mode=mode)


@mcp.tool()
def extract_excel_workbook(source_path: str) -> dict[str, Any]:
    """Process one Excel workbook inside the project root."""
    if not source_path.lower().endswith((".xlsx", ".xlsm")):
        return {
            "status": "error",
            "error": "extract_excel_workbook only supports .xlsx and .xlsm files",
            "source_path": source_path,
        }
    return convert_document_impl(source_path=source_path, mode="fast")


@mcp.tool()
def create_material_index(parsed_dir: str | None = None) -> dict[str, Any]:
    """Create or update material indexes from parsed metadata."""
    return create_material_index_impl(parsed_dir=parsed_dir)


@mcp.tool()
def generate_wiki_candidates(parsed_item_path: str | None = None) -> dict[str, Any]:
    """Generate pending wiki candidate pages from parsed materials."""
    return generate_wiki_candidates_impl(parsed_item_path=parsed_item_path)


@mcp.tool()
def get_workspace_summary() -> dict[str, Any]:
    """Return a concise workspace status summary."""
    from tools.paths import INBOX_DIR, MATERIALS_DIR, PARSED_DIR, WIKI_PENDING_DIR, LOGS_DIR

    recent_logs = []
    if LOGS_DIR.exists():
        recent_logs = [path.name for path in sorted(LOGS_DIR.glob("*"), key=lambda item: item.stat().st_mtime, reverse=True)[:5] if path.is_file()]
    return {
        "status": "ok",
        "inbox_file_count": len([path for path in INBOX_DIR.glob("*") if path.is_file() and not path.name.startswith(".")]),
        "parsed_item_count": len([path for path in PARSED_DIR.rglob("metadata.json") if path.is_file()]),
        "wiki_pending_count": len([path for path in WIKI_PENDING_DIR.glob("*.md") if path.is_file()]),
        "material_index_exists": (MATERIALS_DIR / "material_index.md").exists(),
        "recent_logs": recent_logs,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
