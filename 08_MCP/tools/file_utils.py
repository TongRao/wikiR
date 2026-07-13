"""General file utilities for material processing."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .paths import LOGS_DIR, PARSED_DIR, RAW_ARCHIVE_DIR, ensure_parent, relative_path


SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".xlsx", ".xlsm", ".pptx", ".txt", ".md"}
DEFAULT_CATEGORY = "材料"
CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("申报书", ("申报书", "申请书", "项目申请", "项目申报书", "可行性研究报告", "实施方案")),
    ("报奖", ("报奖", "奖项", "奖励", "科技奖", "成果奖", "提名书", "推荐书")),
    ("政策", ("政策", "通知", "办法", "指南", "规划", "意见", "方案", "申报指南", "项目指南")),
    ("合同", ("合同", "协议", "任务书", "委托书")),
    ("表格", ("表格", "清单", "汇总表", "统计表", "需求表", "xlsx", "xlsm")),
)


def now_iso() -> str:
    """Return a second-precision ISO timestamp."""
    return datetime.now().replace(microsecond=0).isoformat()


def today_parts() -> tuple[str, str, str]:
    """Return current YYYY, MM, and YYYYMMDD strings."""
    now = datetime.now()
    return now.strftime("%Y"), now.strftime("%m"), now.strftime("%Y%m%d")


def sha256_file(path: Path) -> str:
    """Compute the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_attachment_prefix(value: str) -> str:
    """Remove common leading attachment markers while keeping the real title."""
    value = value.strip()
    patterns = (
        r"^[【\[\(\s]*附件\s*[0-9０-９一二三四五六七八九十百]+[】\]\)\s]*[:：._\-—、\s]*",
        r"^[【\[\(\s]*附录\s*[0-9０-９一二三四五六七八九十百]+[】\]\)\s]*[:：._\-—、\s]*",
    )
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    return value.strip()


def clean_material_title(value: str, *, fallback: str = "material") -> str:
    """Return a readable title-like filename stem, preserving Chinese semantics."""
    value = Path(value).stem
    value = strip_attachment_prefix(value)
    value = re.sub(r"[/\\:*?\"<>|]", " ", value)
    value = re.sub(r"[\t\r\n]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" ._-")
    return value[:100] or fallback


def safe_stem(value: str, *, fallback: str = "material") -> str:
    """Return a filesystem-safe stem while preserving Chinese text."""
    value = clean_material_title(value, fallback=fallback)
    value = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:100] or fallback


def safe_filename(path: Path, *, digest: str | None = None) -> str:
    """Return a safe filename preserving the suffix."""
    stem = safe_stem(path.stem)
    suffix = path.suffix.lower()
    if digest:
        stem = f"{stem}_{digest[:8]}"
    return f"{stem}{suffix}"


def classify_material(filename: str, text_hint: str = "") -> str:
    """Classify a material with lightweight local rules.

    This is intentionally deterministic. A future Hermes/Qwen tool can overwrite
    the returned category in metadata, but ingestion should not depend on an LLM.
    """
    text = f"{filename} {text_hint}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword.lower() in text for keyword in keywords):
            return category
    return DEFAULT_CATEGORY


def material_name_info(source_path: Path, digest: str, *, text_hint: str = "") -> dict[str, str]:
    """Build the canonical material naming fields."""
    year, _, date_slug = today_parts()
    clean_title = clean_material_title(source_path.stem)
    category = classify_material(source_path.name, text_hint=text_hint)
    title_stem = safe_stem(clean_title)
    digest_short = digest[:8]
    base_name = f"{category}_{date_slug}_{title_stem}_{digest_short}"
    return {
        "year": year,
        "date": date_slug,
        "category": category,
        "clean_title": clean_title,
        "stem": title_stem,
        "digest_short": digest_short,
        "base_name": base_name,
        "filename": f"{base_name}{source_path.suffix.lower()}",
    }


def parsed_dir_for(source_path: Path, digest: str, *, text_hint: str = "") -> Path:
    """Return a unique parsed directory under 02_parsed/YYYY."""
    info = material_name_info(source_path, digest, text_hint=text_hint)
    parsed_year_dir = PARSED_DIR / info["year"]
    parsed_year_dir.mkdir(parents=True, exist_ok=True)
    return unique_path(parsed_year_dir / info["base_name"])


def safe_sheet_filename(sheet_name: str) -> str:
    """Return a safe CSV filename for an Excel sheet."""
    return f"{safe_stem(sheet_name, fallback='sheet')}.csv"


def unique_path(path: Path) -> Path:
    """Return a non-existing path by adding timestamp/counter suffixes when needed."""
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = path.with_name(f"{path.stem}_{stamp}{path.suffix}")
    counter = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}_{stamp}_{counter}{path.suffix}")
        counter += 1
    return candidate


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON object with stable formatting."""
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text, creating parent directories as needed."""
    ensure_parent(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_text_lossy(path: Path) -> str:
    """Read text with common encodings and replacement fallback."""
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def write_csv(path: Path, rows: Iterable[Iterable[Any]]) -> None:
    """Write rows to a UTF-8-sig CSV file."""
    ensure_parent(path)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow(["" if value is None else value for value in row])


def create_processing_paths(source_path: Path, digest: str) -> dict[str, Path | str]:
    """Create parsed item directories and return standard output paths."""
    parsed_dir = parsed_dir_for(source_path, digest)
    source_dir = parsed_dir / "source"
    tables_dir = parsed_dir / "tables"
    images_dir = parsed_dir / "images"
    source_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    safe_source_name = material_name_info(source_path, digest)["filename"]
    return {
        "parsed_dir": parsed_dir,
        "source_dir": source_dir,
        "tables_dir": tables_dir,
        "images_dir": images_dir,
        "source_copy_path": source_dir / safe_source_name,
        "document_path": parsed_dir / "document.md",
        "metadata_path": parsed_dir / "metadata.json",
        "report_path": parsed_dir / "processing_report.md",
        "safe_source_name": safe_source_name,
    }


def processing_paths_for_dir(parsed_dir: Path, source_path: Path, digest: str) -> dict[str, Path | str]:
    """Return standard output paths inside an already-created parsed directory."""
    source_dir = parsed_dir / "source"
    tables_dir = parsed_dir / "tables"
    images_dir = parsed_dir / "images"
    source_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    safe_source_name = material_name_info(source_path, digest)["filename"]
    return {
        "parsed_dir": parsed_dir,
        "source_dir": source_dir,
        "tables_dir": tables_dir,
        "images_dir": images_dir,
        "source_copy_path": source_dir / safe_source_name,
        "document_path": parsed_dir / "document.md",
        "metadata_path": parsed_dir / "metadata.json",
        "report_path": parsed_dir / "processing_report.md",
        "safe_source_name": safe_source_name,
    }


def archive_path_for(source_path: Path, digest: str, *, text_hint: str = "") -> Path:
    """Return a unique archive path under 01_raw_archive/YYYY."""
    info = material_name_info(source_path, digest, text_hint=text_hint)
    archive_dir = RAW_ARCHIVE_DIR / info["year"]
    archive_dir.mkdir(parents=True, exist_ok=True)
    return unique_path(archive_dir / info["filename"])


def copy_source_to_parsed(source_path: Path, destination: Path) -> None:
    """Copy the original source into the parsed item source folder."""
    ensure_parent(destination)
    shutil.copy2(source_path, destination)


def archive_original(source_path: Path, destination: Path, *, move: bool) -> None:
    """Archive an original file by moving or copying it."""
    ensure_parent(destination)
    if move:
        shutil.move(str(source_path), str(destination))
    else:
        shutil.copy2(source_path, destination)


def make_report(title: str, status: str, lines: list[str]) -> str:
    """Create a standard processing report body."""
    body = [f"# Processing Report: {title}", "", f"- status: {status}", f"- processed_at: {now_iso()}", ""]
    body.extend(lines)
    return "\n".join(body)


def result_paths(parsed_dir: Path, document_path: Path, metadata_path: Path, archive_path: Path) -> dict[str, str]:
    """Return common relative path fields for tool responses."""
    return {
        "parsed_dir": relative_path(parsed_dir),
        "markdown_path": relative_path(document_path),
        "metadata_path": relative_path(metadata_path),
        "archive_path": relative_path(archive_path),
    }


def write_failure_log(original_filename: str, error: str, *, digest: str | None = None) -> Path:
    """Write a concise failure log under 06_logs and return its path."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = safe_stem(Path(original_filename).stem)
    suffix = digest[:8] if digest else "error"
    log_path = unique_path(LOGS_DIR / f"{stamp}_{stem}_{suffix}.md")
    write_text(
        log_path,
        "\n".join(
            [
                f"# Processing Failure: {original_filename}",
                "",
                f"- status: error",
                f"- failed_at: {now_iso()}",
                f"- sha256: {digest or ''}",
                "",
                "## Error",
                "",
                "```text",
                error,
                "```",
            ]
        ),
    )
    return log_path
