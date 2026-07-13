"""Material index generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .file_utils import read_json, write_json, write_text
from .paths import MATERIALS_DIR, PARSED_DIR, WIKI_INDEX_DIR, relative_path, resolve_workspace_path


def create_material_index(parsed_dir: str | None = None) -> dict[str, Any]:
    """Generate material_index.md/json and wiki/05_index/source_index.md from parsed metadata."""
    metadata_files = find_metadata_files(parsed_dir)
    items = [metadata_to_index_item(path) for path in metadata_files]
    items.sort(key=lambda item: item.get("processed_at", ""), reverse=True)

    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
    WIKI_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    json_path = MATERIALS_DIR / "material_index.json"
    md_path = MATERIALS_DIR / "material_index.md"
    wiki_index_path = WIKI_INDEX_DIR / "source_index.md"

    write_json(json_path, {"items": items, "count": len(items)})
    markdown = render_material_index_markdown(items)
    write_text(md_path, markdown)
    write_text(wiki_index_path, render_wiki_source_index(items))

    return {
        "status": "ok",
        "count": len(items),
        "material_index_md": relative_path(md_path),
        "material_index_json": relative_path(json_path),
        "wiki_source_index": relative_path(wiki_index_path),
    }


def find_metadata_files(parsed_dir: str | None) -> list[Path]:
    """Find metadata files from all parsed items or one parsed directory."""
    if parsed_dir:
        target = resolve_workspace_path(parsed_dir, must_exist=True)
        if target.is_file() and target.name == "metadata.json":
            return [target]
        if target.is_dir():
            metadata = target / "metadata.json"
            return [metadata] if metadata.exists() else sorted(target.rglob("metadata.json"))
        return []
    return sorted(PARSED_DIR.rglob("metadata.json"))


def metadata_to_index_item(metadata_path: Path) -> dict[str, Any]:
    """Convert one metadata.json file into a material index item."""
    metadata = read_json(metadata_path)
    parsed_dir = metadata_path.parent
    document_path = parsed_dir / "document.md"
    title = metadata.get("title") or metadata.get("original_filename") or parsed_dir.name
    return {
        "title": title,
        "category": metadata.get("category", ""),
        "clean_title": metadata.get("clean_title", title),
        "original_filename": metadata.get("original_filename", ""),
        "file_type": metadata.get("file_type", ""),
        "parsed_markdown_path": relative_path(document_path) if document_path.exists() else "",
        "archive_path": metadata.get("archive_path", ""),
        "processed_at": metadata.get("processed_at", ""),
        "sha256": metadata.get("sha256", ""),
        "suggested_topics": suggest_topics(title, metadata.get("original_filename", "")),
        "suggested_project": "",
        "status": metadata.get("status", "unknown"),
        "metadata_path": relative_path(metadata_path),
    }


def suggest_topics(title: str, filename: str) -> list[str]:
    """Return simple first-version topic hints."""
    text = f"{title} {filename}".lower()
    topics: list[str] = []
    rules = {
        "ai_tech": ["ai", "人工智能", "模型", "llm", "算法"],
        "power_grid": ["电网", "变电", "输电", "配电", "能源"],
        "project_application": ["申报", "申请书", "项目", "指南", "proposal"],
        "writing_methods": ["写作", "模板", "报告", "总结"],
    }
    for topic, keywords in rules.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    return topics


def render_material_index_markdown(items: list[dict[str, Any]]) -> str:
    """Render the material index Markdown file."""
    lines = ["# Material Index", "", f"Total materials: {len(items)}", ""]
    for item in items:
        lines.extend(
            [
                f"## {item['title']}",
                "",
                f"- original_filename: {item['original_filename']}",
                f"- category: {item['category']}",
                f"- file_type: {item['file_type']}",
                f"- status: {item['status']}",
                f"- processed_at: {item['processed_at']}",
                f"- parsed_markdown_path: `{item['parsed_markdown_path']}`",
                f"- archive_path: `{item['archive_path']}`",
                f"- sha256: `{item['sha256']}`",
                f"- suggested_topics: {', '.join(item['suggested_topics']) if item['suggested_topics'] else ''}",
                "",
            ]
        )
    return "\n".join(lines)


def render_wiki_source_index(items: list[dict[str, Any]]) -> str:
    """Render an Obsidian-friendly source index."""
    lines = [
        "---",
        "type: index",
        "created_by: material_mcp",
        "tags:",
        "  - index",
        "---",
        "# Source Index",
        "",
    ]
    for item in items:
        lines.extend(
            [
                f"## {item['title']}",
                "",
                f"- Status: {item['status']}",
                f"- Category: {item['category']}",
                f"- Parsed Markdown: `{item['parsed_markdown_path']}`",
                f"- Archive: `{item['archive_path']}`",
                "",
            ]
        )
    return "\n".join(lines)
