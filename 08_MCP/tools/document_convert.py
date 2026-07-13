"""Document conversion tool implementation."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .excel_extract import extract_excel_to_parsed
from .file_utils import (
    SUPPORTED_EXTENSIONS,
    archive_original,
    archive_path_for,
    copy_source_to_parsed,
    make_report,
    material_name_info,
    now_iso,
    parsed_dir_for,
    processing_paths_for_dir,
    read_text_lossy,
    result_paths,
    safe_stem,
    sha256_file,
    write_failure_log,
    write_json,
    write_text,
)
from .paths import INBOX_DIR, PROJECT_ROOT, relative_path, resolve_workspace_path


def convert_document(source_path: str, mode: str = "fast") -> dict[str, Any]:
    """Convert one supported source file into a parsed item directory.

    The conversion is transactional: parsed outputs and archive movement only happen
    after conversion succeeds. Failed inbox files remain in 00_inbox.
    """
    source = resolve_workspace_path(source_path, must_exist=True)
    if not source.is_file():
        raise IsADirectoryError(f"Source is not a file: {relative_path(source)}")
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return {
            "status": "error",
            "error": f"Unsupported file type: {suffix}",
            "source_path": relative_path(source),
        }

    digest = sha256_file(source)
    name_info = material_name_info(source, digest)
    (PROJECT_ROOT / ".tmp").mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="wikir_parse_", dir=str(PROJECT_ROOT / ".tmp")))
    paths = processing_paths_for_dir(temp_root / "parsed_item", source, digest)
    temp_parsed_dir = paths["parsed_dir"]
    temp_source_copy_path = paths["source_copy_path"]
    document_path = paths["document_path"]
    metadata_path = paths["metadata_path"]
    report_path = paths["report_path"]

    assert isinstance(temp_parsed_dir, Path)
    assert isinstance(temp_source_copy_path, Path)
    assert isinstance(document_path, Path)
    assert isinstance(metadata_path, Path)
    assert isinstance(report_path, Path)

    copy_source_to_parsed(source, temp_source_copy_path)

    metadata_base = {
        "title": name_info["clean_title"],
        "clean_title": name_info["clean_title"],
        "category": name_info["category"],
        "material_date": name_info["date"],
        "normalized_name": name_info["base_name"],
        "original_filename": source.name,
        "safe_filename": paths["safe_source_name"],
        "file_type": suffix,
        "mode": mode,
        "sha256": digest,
        "workspace_root": str(PROJECT_ROOT.resolve()),
        "source_copy_path": "",
        "archive_path": "",
        "parsed_dir": "",
    }

    try:
        if suffix in {".xlsx", ".xlsm"}:
            conversion = extract_excel_to_parsed(
                temp_source_copy_path,
                parsed_dir=temp_parsed_dir,
                tables_dir=temp_parsed_dir / "tables",
                document_path=document_path,
                metadata_path=metadata_path,
                report_path=report_path,
                metadata_base=metadata_base,
            )
        elif suffix in {".txt", ".md"}:
            conversion = convert_text_file(temp_source_copy_path, document_path, metadata_path, report_path, metadata_base)
        else:
            conversion = convert_with_markitdown(temp_source_copy_path, document_path, metadata_path, report_path, metadata_base, mode=mode)
    except Exception as exc:
        conversion = {"status": "error", "converter": "unknown", "error": f"Unhandled conversion error: {exc}"}

    if conversion.get("status") != "ok":
        error = str(conversion.get("error") or "Conversion failed")
        log_path = write_failure_log(source.name, error, digest=digest)
        cleanup_temp_dir(temp_root)
        return {
            "original_filename": source.name,
            "status": "error",
            "source_path": relative_path(source),
            "sha256": digest,
            "converter": conversion.get("converter"),
            "error": error,
            "failure_log_path": relative_path(log_path),
            "kept_in_inbox": source.parent.resolve() == INBOX_DIR.resolve(),
        }

    content_hint = read_document_hint(document_path)
    final_name_info = material_name_info(source, digest, text_hint=content_hint)
    final_source_name = final_name_info["filename"]
    if temp_source_copy_path.name != final_source_name:
        renamed_source_copy_path = temp_source_copy_path.with_name(final_source_name)
        temp_source_copy_path.replace(renamed_source_copy_path)
        temp_source_copy_path = renamed_source_copy_path

    final_parsed_dir = parsed_dir_for(source, digest, text_hint=content_hint)
    temp_parsed_dir.replace(final_parsed_dir)
    cleanup_temp_dir(temp_root)
    archive_path = archive_path_for(source, digest, text_hint=content_hint)
    move_to_archive = source.parent.resolve() == INBOX_DIR.resolve()
    archive_original(source, archive_path, move=move_to_archive)

    final_source_copy_path = final_parsed_dir / "source" / final_source_name
    final_document_path = final_parsed_dir / "document.md"
    final_metadata_path = final_parsed_dir / "metadata.json"
    final_report_path = final_parsed_dir / "processing_report.md"
    patch_success_metadata(final_metadata_path, final_parsed_dir, final_source_copy_path, archive_path, final_name_info)
    patch_success_markdown(final_document_path, final_source_copy_path)

    common_paths = result_paths(final_parsed_dir, final_document_path, final_metadata_path, archive_path)
    return {
        "original_filename": metadata_base["original_filename"],
        "status": "ok",
        **common_paths,
        "source_copy_path": relative_path(final_source_copy_path),
        "processing_report_path": relative_path(final_report_path),
        "sha256": digest,
        "converter": conversion.get("converter"),
        "error": None,
    }


def title_from_source(source: Path) -> str:
    """Create a readable title from a source filename."""
    title = source.stem.replace("_", " ").replace("-", " ").strip()
    return title or safe_stem(source.stem)


def read_document_hint(document_path: Path, limit: int = 6000) -> str:
    """Read a short converted-text sample for post-conversion classification."""
    try:
        return document_path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def convert_text_file(
    source_path: Path,
    document_path: Path,
    metadata_path: Path,
    report_path: Path,
    metadata_base: dict[str, Any],
) -> dict[str, Any]:
    """Convert a text/Markdown file by wrapping it with source frontmatter."""
    raw_text = read_text_lossy(source_path)
    markdown = "\n".join(
        [
            "---",
            "type: parsed_document",
            f"source_file: {metadata_base['source_copy_path']}",
            f"original_filename: {metadata_base['original_filename']}",
            f"sha256: {metadata_base['sha256']}",
            "---",
            "",
            f"# {metadata_base['title']}",
            "",
            raw_text,
        ]
    )
    metadata = {
        **metadata_base,
        "status": "ok",
        "converter": "direct_text",
        "processed_at": now_iso(),
    }
    write_text(document_path, markdown)
    write_json(metadata_path, metadata)
    write_text(report_path, make_report(metadata_base["title"], "ok", ["- converter: direct_text"]))
    return {"status": "ok", "converter": "direct_text"}


def convert_with_markitdown(
    source_path: Path,
    document_path: Path,
    metadata_path: Path,
    report_path: Path,
    metadata_base: dict[str, Any],
    *,
    mode: str,
) -> dict[str, Any]:
    """Convert a document with MarkItDown Python API or CLI fallback."""
    markdown = ""
    converter = "markitdown"
    stderr = ""

    try:
        from markitdown import MarkItDown  # type: ignore

        result = MarkItDown().convert(str(source_path))
        markdown = getattr(result, "text_content", "") or str(result)
        converter = "markitdown-python"
    except Exception as api_exc:
        cli_result = run_markitdown_cli(source_path)
        markdown = cli_result["stdout"]
        stderr = f"Python API failed: {api_exc}\n{cli_result['stderr']}".strip()
        converter = "markitdown-cli"
        if cli_result["returncode"] != 0 or not markdown.strip():
            return write_conversion_error(
                document_path,
                metadata_path,
                report_path,
                metadata_base,
                f"MarkItDown conversion failed. {stderr}".strip(),
            )

    markdown = markdown.strip()
    if not markdown:
        return write_conversion_error(document_path, metadata_path, report_path, metadata_base, "MarkItDown returned empty markdown.")

    metadata = {
        **metadata_base,
        "status": "ok",
        "converter": converter,
        "processed_at": now_iso(),
    }
    document_body = "\n".join(
        [
            "---",
            "type: parsed_document",
            f"source_file: {metadata_base['source_copy_path']}",
            f"original_filename: {metadata_base['original_filename']}",
            f"sha256: {metadata_base['sha256']}",
            f"converter: {converter}",
            "---",
            "",
            markdown,
        ]
    )
    write_text(document_path, document_body)
    write_json(metadata_path, metadata)
    report_lines = [f"- converter: {converter}", f"- mode: {mode}"]
    if stderr:
        report_lines.extend(["", "## Converter Notes", "", "```text", stderr, "```"])
    write_text(report_path, make_report(metadata_base["title"], "ok", report_lines))
    return {"status": "ok", "converter": converter}


def run_markitdown_cli(source_path: Path) -> dict[str, Any]:
    """Run the markitdown CLI and capture stdout/stderr."""
    try:
        proc = subprocess.run(
            ["markitdown", str(source_path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    except FileNotFoundError:
        return {"returncode": 127, "stdout": "", "stderr": "markitdown CLI not found"}
    return {"returncode": proc.returncode, "stdout": proc.stdout or "", "stderr": proc.stderr or ""}


def write_conversion_error(
    document_path: Path,
    metadata_path: Path,
    report_path: Path,
    metadata_base: dict[str, Any],
    error: str,
) -> dict[str, Any]:
    """Write standard error outputs for a conversion failure."""
    metadata = {
        **metadata_base,
        "status": "error",
        "converter": "markitdown",
        "processed_at": now_iso(),
        "error": error,
    }
    write_text(document_path, f"# {metadata_base['title']}\n\nConversion failed.\n")
    write_json(metadata_path, metadata)
    write_text(report_path, make_report(metadata_base["title"], "error", [f"- error: {error}"]))
    return {"status": "error", "converter": "markitdown", "error": error}


def cleanup_temp_dir(path: Path) -> None:
    """Remove a temporary parse directory."""
    import shutil

    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def patch_success_metadata(
    metadata_path: Path,
    parsed_dir: Path,
    source_copy_path: Path,
    archive_path: Path,
    name_info: dict[str, str],
) -> None:
    """Patch final relative paths into successful metadata."""
    import json

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["title"] = name_info["clean_title"]
    metadata["clean_title"] = name_info["clean_title"]
    metadata["category"] = name_info["category"]
    metadata["material_date"] = name_info["date"]
    metadata["normalized_name"] = name_info["base_name"]
    metadata["safe_filename"] = name_info["filename"]
    metadata["parsed_dir"] = relative_path(parsed_dir)
    metadata["source_copy_path"] = relative_path(source_copy_path)
    metadata["archive_path"] = relative_path(archive_path)
    write_json(metadata_path, metadata)


def patch_success_markdown(document_path: Path, source_copy_path: Path) -> None:
    """Patch placeholder source_file fields in parsed Markdown."""
    text = document_path.read_text(encoding="utf-8")
    text = text.replace("source_file: \n", f"source_file: {relative_path(source_copy_path)}\n")
    document_path.write_text(text, encoding="utf-8")
