"""Wiki candidate page generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .file_utils import read_json, safe_stem, unique_path, write_text
from .paths import PARSED_DIR, WIKI_PENDING_DIR, relative_path, resolve_workspace_path


def generate_wiki_candidates(parsed_item_path: str | None = None) -> dict[str, Any]:
    """Generate pending wiki page skeletons from parsed metadata."""
    metadata_files = find_candidate_metadata(parsed_item_path)
    WIKI_PENDING_DIR.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []

    for metadata_path in metadata_files:
        metadata = read_json(metadata_path)
        title = metadata.get("title") or metadata.get("original_filename") or metadata_path.parent.name
        topic = safe_stem(title, fallback="example_topic")
        page_path = unique_path(WIKI_PENDING_DIR / f"{topic}.md")
        document_path = metadata_path.parent / "document.md"
        body = render_candidate_page(title, topic, document_path)
        write_text(page_path, body)
        items.append(
            {
                "title": title,
                "status": "ok",
                "wiki_candidate_path": relative_path(page_path),
                "source_markdown_path": relative_path(document_path) if document_path.exists() else "",
            }
        )

    return {"status": "ok", "generated_count": len(items), "items": items}


def find_candidate_metadata(parsed_item_path: str | None) -> list[Path]:
    """Find metadata files for wiki candidate generation."""
    if parsed_item_path:
        target = resolve_workspace_path(parsed_item_path, must_exist=True)
        if target.is_file() and target.name == "metadata.json":
            return [target]
        if target.is_dir():
            metadata = target / "metadata.json"
            return [metadata] if metadata.exists() else sorted(target.rglob("metadata.json"))
        return []
    return sorted(PARSED_DIR.rglob("metadata.json"))


def render_candidate_page(title: str, topic: str, document_path: Path) -> str:
    """Render a pending wiki candidate skeleton."""
    source = relative_path(document_path) if document_path.exists() else ""
    return f"""---
type: wiki
domain: pending
topic: {topic}
source_files:
  - {source}
source_project: pending
review_status: pending
created_by: material_mcp
tags:
  - pending
---
# {title}

## 1. Brief Definition

## 2. Business Context

## 3. Technical Route

## 4. Reusable Writing

## 5. Related Projects

## 6. Notes and Risks

## 7. Sources

- `{source}`
"""
