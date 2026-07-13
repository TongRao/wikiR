"""Inbox processing orchestration."""

from __future__ import annotations

from typing import Any

from .document_convert import convert_document
from .file_utils import SUPPORTED_EXTENSIONS
from .paths import INBOX_DIR, init_workspace_files, relative_path


def process_inbox(mode: str = "fast") -> dict[str, Any]:
    """Process all supported files currently in 00_inbox."""
    init_workspace_files(overwrite=False)
    items: list[dict[str, Any]] = []
    failed_count = 0
    processed_count = 0

    files = [path for path in sorted(INBOX_DIR.iterdir()) if path.is_file() and not path.name.startswith(".")]
    for source in files:
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            items.append(
                {
                    "original_filename": source.name,
                    "status": "skipped",
                    "reason": f"Unsupported file type: {source.suffix.lower()}",
                    "source_path": relative_path(source),
                }
            )
            continue
        try:
            result = convert_document(relative_path(source), mode=mode)
        except Exception as exc:
            failed_count += 1
            items.append(
                {
                    "original_filename": source.name,
                    "status": "error",
                    "error": str(exc),
                    "source_path": relative_path(source) if source.exists() else source.name,
                }
            )
            continue
        if result.get("status") == "ok":
            processed_count += 1
        else:
            failed_count += 1
        items.append(result)

    return {
        "status": "ok" if failed_count == 0 else "partial_error",
        "processed_count": processed_count,
        "failed_count": failed_count,
        "items": items,
    }

