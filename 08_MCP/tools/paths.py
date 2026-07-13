"""Workspace path utilities and initialization helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INBOX_DIR = PROJECT_ROOT / "00_inbox"
RAW_ARCHIVE_DIR = PROJECT_ROOT / "01_raw_archive"
PARSED_DIR = PROJECT_ROOT / "02_parsed"
MATERIALS_DIR = PROJECT_ROOT / "03_materials"
WIKI_DIR = PROJECT_ROOT / "wiki"
DRAFTS_DIR = PROJECT_ROOT / "05_drafts"
LOGS_DIR = PROJECT_ROOT / "06_logs"
CONFIG_DIR = PROJECT_ROOT / "07_config"
MCP_DIR = PROJECT_ROOT / "08_MCP"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

WIKI_WIKI_DIR = WIKI_DIR / "01_wiki"
WIKI_PENDING_DIR = WIKI_WIKI_DIR / "_pending"
WIKI_PROJECTS_DIR = WIKI_DIR / "02_projects"
WIKI_REUSABLE_DIR = WIKI_DIR / "03_reusable"
WIKI_TEMPLATES_DIR = WIKI_DIR / "04_templates"
WIKI_INDEX_DIR = WIKI_DIR / "05_index"
WIKI_ATTACHMENTS_DIR = WIKI_DIR / "99_attachments"

REQUIRED_DIRECTORIES = [
    INBOX_DIR,
    RAW_ARCHIVE_DIR,
    PARSED_DIR,
    MATERIALS_DIR,
    WIKI_DIR,
    WIKI_WIKI_DIR,
    WIKI_WIKI_DIR / "ai_tech",
    WIKI_WIKI_DIR / "power_grid",
    WIKI_WIKI_DIR / "writing_methods",
    WIKI_PENDING_DIR,
    WIKI_PROJECTS_DIR,
    WIKI_REUSABLE_DIR,
    WIKI_REUSABLE_DIR / "_pending",
    WIKI_REUSABLE_DIR / "technical_routes",
    WIKI_REUSABLE_DIR / "result_indicators",
    WIKI_REUSABLE_DIR / "common_phrases",
    WIKI_TEMPLATES_DIR,
    WIKI_INDEX_DIR,
    WIKI_ATTACHMENTS_DIR,
    DRAFTS_DIR,
    LOGS_DIR,
    CONFIG_DIR,
    MCP_DIR,
    MCP_DIR / "tools",
    SCRIPTS_DIR,
]


class WorkspaceSecurityError(ValueError):
    """Raised when a path attempts to escape the project root."""


def relative_path(path: Path) -> str:
    """Return a POSIX relative path from the project root."""
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def path_payload(path: Path) -> dict[str, str]:
    """Return both relative and absolute path strings for JSON responses."""
    resolved = path.resolve()
    return {
        "relative": relative_path(resolved),
        "absolute": str(resolved),
    }


def resolve_workspace_path(path_value: str | Path, *, must_exist: bool = False) -> Path:
    """Resolve a user-provided path and ensure it stays inside the project root."""
    raw = Path(path_value).expanduser()
    candidate = raw if raw.is_absolute() else PROJECT_ROOT / raw
    resolved = candidate.resolve(strict=False)
    root = PROJECT_ROOT.resolve()
    if not resolved.is_relative_to(root):
        raise WorkspaceSecurityError(f"Path is outside workspace root: {path_value}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {relative_path(resolved)}")
    return resolved


def ensure_parent(path: Path) -> None:
    """Create a file parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text_if_needed(path: Path, content: str, *, overwrite: bool = False) -> bool:
    """Write text to a file unless it exists and overwrite is false."""
    ensure_parent(path)
    if path.exists() and not overwrite:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def init_workspace_files(overwrite: bool = False) -> dict[str, Any]:
    """Create required directories and base files."""
    created_dirs: list[str] = []
    skipped_dirs: list[str] = []
    created_files: list[str] = []
    skipped_files: list[str] = []

    for directory in REQUIRED_DIRECTORIES:
        if directory.exists():
            skipped_dirs.append(relative_path(directory))
        else:
            directory.mkdir(parents=True, exist_ok=True)
            created_dirs.append(relative_path(directory))

    files = {
        WIKI_DIR / "00_home.md": WIKI_HOME,
        WIKI_TEMPLATES_DIR / "wiki_page_template.md": WIKI_PAGE_TEMPLATE,
        WIKI_TEMPLATES_DIR / "project_page_template.md": PROJECT_PAGE_TEMPLATE,
        PROJECT_ROOT / "AGENTS.md": AGENTS_TEMPLATE,
        PROJECT_ROOT / "README.md": README_TEMPLATE,
        PROJECT_ROOT / ".gitignore": GITIGNORE_TEMPLATE,
    }
    for path, content in files.items():
        if write_text_if_needed(path, content, overwrite=overwrite):
            created_files.append(relative_path(path))
        else:
            skipped_files.append(relative_path(path))

    return {
        "created_dirs": created_dirs,
        "skipped_dirs": skipped_dirs,
        "created_files": created_files,
        "skipped_files": skipped_files,
    }


def directory_status() -> dict[str, bool]:
    """Return key directory existence flags for health checks."""
    return {
        "inbox": INBOX_DIR.exists(),
        "raw_archive": RAW_ARCHIVE_DIR.exists(),
        "parsed": PARSED_DIR.exists(),
        "materials": MATERIALS_DIR.exists(),
        "wiki": WIKI_DIR.exists(),
        "mcp": MCP_DIR.exists(),
    }


WIKI_HOME = """---
type: home
review_status: active
created_by: wikiR
tags:
  - home
---
# wikiR Home

This Obsidian vault contains curated wiki pages, project pages, reusable writing fragments, templates, and indexes generated from local materials.
"""

WIKI_PAGE_TEMPLATE = """---
type: wiki
domain: pending
topic: pending
source_files: []
source_project: pending
review_status: pending
created_by: template
tags:
  - pending
---
# Topic Title

## 1. Brief Definition

## 2. Business Context

## 3. Technical Route

## 4. Reusable Writing

## 5. Related Projects

## 6. Notes and Risks

## 7. Sources
"""

PROJECT_PAGE_TEMPLATE = """---
type: project
project_status: pending
source_files: []
review_status: pending
created_by: template
tags:
  - project
---
# Project Title

## 1. Background

## 2. Objectives

## 3. Materials

## 4. Technical Route

## 5. Deliverables

## 6. Risks

## 7. Sources
"""

AGENTS_TEMPLATE = """# wikiR Agent Guide

wikiR is a local material-management workspace for document parsing, material archiving, wiki generation, and Obsidian use. Hermes should work inside this project root and use the project MCP server for file processing.

See README.md for setup and safety boundaries.
"""

README_TEMPLATE = """# wikiR

Local material-management workspace for Hermes Agent, document parsing, material archiving, wiki generation, and Obsidian-based review.
"""

GITIGNORE_TEMPLATE = """.DS_Store
__pycache__/
.venv/
.env
*.log
*.tmp
*.gguf
*.safetensors
*.bin
*.pt
*.pth
*.onnx
06_logs/*
!06_logs/.gitkeep
01_raw_archive/*
!01_raw_archive/.gitkeep
00_inbox/*
!00_inbox/.gitkeep
02_parsed/*
!02_parsed/.gitkeep
05_drafts/*
!05_drafts/.gitkeep
"""
