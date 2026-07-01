#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "harness" / "config.json"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]#|]+)")
TOKEN_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]+", re.I)
SAFE_NAME_RE = re.compile(r"[#\|\^:\[\]%/\\]+")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raise SystemExit(f"Missing config: {CONFIG_PATH}")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def today() -> str:
    return dt.date.today().isoformat()


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def ensure_dirs(config: dict) -> None:
    for value in config["paths"].values():
        (ROOT / value).mkdir(parents=True, exist_ok=True)


def read_text_lossy(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def extract_zip_xml_text(path: Path) -> str:
    parts: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            names = [
                name
                for name in zf.namelist()
                if name.endswith(".xml")
                and (
                    name.startswith("word/")
                    or name.startswith("ppt/")
                    or name.startswith("xl/sharedStrings")
                )
            ]
            for name in names[:80]:
                try:
                    root = ET.fromstring(zf.read(name))
                except ET.ParseError:
                    continue
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        parts.append(elem.text.strip())
    except zipfile.BadZipFile:
        return ""
    return "\n".join(parts)


def extract_pdf_text(path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return ""
    proc = subprocess.run(
        [pdftotext, str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.stdout if proc.returncode == 0 else ""


def extract_text(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in {
        ".md",
        ".txt",
        ".csv",
        ".tsv",
        ".json",
        ".jsonl",
        ".yaml",
        ".yml",
        ".log",
        ".py",
        ".js",
        ".ts",
        ".html",
        ".htm",
    }:
        text = read_text_lossy(path)
        if suffix in {".html", ".htm"}:
            text = strip_html(text)
        return text, "text"
    if suffix in {".docx", ".pptx", ".xlsx"}:
        return extract_zip_xml_text(path), "office-xml"
    if suffix == ".pdf":
        return extract_pdf_text(path), "pdftotext"
    return "", "unsupported"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_slug(value: str, fallback: str = "untitled") -> str:
    value = SAFE_NAME_RE.sub(" ", value)
    value = re.sub(r"\s+", "-", value.strip())
    value = value.strip(".-_")
    return value[:80] or fallback


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, object] = {}
    current_key = ""
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            result.setdefault(current_key, [])
            if isinstance(result[current_key], list):
                result[current_key].append(line[4:].strip().strip('"'))
            continue
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value == "[]":
                result[current_key] = []
            elif value.startswith('"') and value.endswith('"'):
                result[current_key] = value[1:-1]
            else:
                result[current_key] = value
    return result


def remove_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for match in TOKEN_RE.finditer(text.lower()):
        token = match.group(0)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(token)
            if len(token) > 1:
                tokens.extend(token[i : i + 2] for i in range(len(token) - 1))
        elif len(token) > 1 or token.isdigit():
            tokens.append(token)
    return tokens


def note_paths(config: dict) -> list[Path]:
    paths: list[Path] = []
    for key in ("sources", "notes", "projects", "outputs"):
        base = ROOT / config["paths"][key]
        if base.exists():
            paths.extend(sorted(base.rglob("*.md")))
    return paths


def split_chunks(text: str, chunk_chars: int, overlap: int) -> list[tuple[str, str]]:
    body = remove_frontmatter(text)
    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = []
    heading = "正文"
    buf: list[str] = []
    for line in lines:
        if line.startswith("#"):
            if buf:
                sections.append((heading, buf))
                buf = []
            heading = line.lstrip("#").strip() or "正文"
        else:
            buf.append(line)
    if buf:
        sections.append((heading, buf))

    chunks: list[tuple[str, str]] = []
    for section_heading, section_lines in sections:
        section_text = "\n".join(section_lines).strip()
        if not section_text:
            continue
        start = 0
        while start < len(section_text):
            end = min(start + chunk_chars, len(section_text))
            chunk = section_text[start:end].strip()
            if chunk:
                chunks.append((section_heading, chunk))
            if end == len(section_text):
                break
            start = max(end - overlap, start + 1)
    return chunks


def build_index(args: argparse.Namespace) -> int:
    config = load_config()
    ensure_dirs(config)
    index_dir = ROOT / config["paths"]["index"]
    index_path = index_dir / "wiki_index.jsonl"
    meta_path = index_dir / "wiki_index_meta.json"
    chunk_chars = int(config["index"]["chunk_chars"])
    overlap = int(config["index"]["chunk_overlap"])

    rows = []
    for path in note_paths(config):
        text = read_text_lossy(path)
        fm = parse_frontmatter(text)
        title = first_heading(text) or path.stem
        for idx, (heading, chunk) in enumerate(split_chunks(text, chunk_chars, overlap), start=1):
            payload = f"{title}\n{heading}\n{chunk}"
            tokens = tokenize(payload)
            if not tokens:
                continue
            chunk_id = hashlib.sha1(f"{rel(path)}:{idx}:{chunk[:80]}".encode("utf-8")).hexdigest()[:12]
            rows.append(
                {
                    "id": chunk_id,
                    "path": rel(path),
                    "title": title,
                    "heading": heading,
                    "type": fm.get("type", ""),
                    "status": fm.get("status", ""),
                    "tags": fm.get("tags", []),
                    "text": chunk,
                    "tokens": tokens,
                    "token_count": len(tokens),
                    "mtime": int(path.stat().st_mtime),
                }
            )

    with index_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    meta_path.write_text(
        json.dumps(
            {
                "generated_at": now_iso(),
                "chunk_count": len(rows),
                "note_count": len(note_paths(config)),
                "index_path": rel(index_path),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Indexed {len(rows)} chunks -> {rel(index_path)}")
    return 0


def first_heading(text: str) -> str:
    for line in remove_frontmatter(text).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def load_index(config: dict) -> list[dict]:
    index_path = ROOT / config["paths"]["index"] / "wiki_index.jsonl"
    if not index_path.exists():
        raise SystemExit("Index missing. Run: python3 harness/wiki.py build-index")
    rows = []
    with index_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def search_rows(rows: list[dict], query: str, top_k: int) -> list[dict]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    doc_freq: collections.Counter[str] = collections.Counter()
    token_counts = []
    for row in rows:
        tokens = row.get("tokens", [])
        token_counts.append(len(tokens))
        doc_freq.update(set(tokens))
    total = len(rows) or 1
    avgdl = sum(token_counts) / total if token_counts else 1.0
    q_counts = collections.Counter(query_tokens)
    scored = []
    for row in rows:
        counts = collections.Counter(row.get("tokens", []))
        dl = max(row.get("token_count", 0), 1)
        score = 0.0
        for token, qtf in q_counts.items():
            tf = counts.get(token, 0)
            if not tf:
                continue
            df = doc_freq[token]
            idf = math.log(1 + (total - df + 0.5) / (df + 0.5))
            k1 = 1.5
            b = 0.75
            score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))) * qtf
        haystack = " ".join(
            [
                row.get("path", ""),
                row.get("title", ""),
                row.get("heading", ""),
                " ".join(row.get("tags", [])) if isinstance(row.get("tags"), list) else str(row.get("tags", "")),
            ]
        ).lower()
        if query.lower() in haystack:
            score += 2.0
        if score > 0:
            item = dict(row)
            item["score"] = round(score, 4)
            scored.append(item)
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def excerpt(text: str, max_len: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def cmd_search(args: argparse.Namespace) -> int:
    config = load_config()
    rows = load_index(config)
    top_k = args.top_k or int(config["index"]["top_k"])
    results = search_rows(rows, args.query, top_k)
    for idx, row in enumerate(results, start=1):
        print(f"{idx}. score={row['score']} {row['path']} :: {row['heading']}")
        print(f"   {excerpt(row['text'])}")
    if not results:
        print("No results.")
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    config = load_config()
    ensure_dirs(config)
    rows = load_index(config)
    top_k = args.top_k or int(config["index"]["top_k"])
    results = search_rows(rows, args.query, top_k)
    out_path = ROOT / config["paths"]["context"] / "last_context.md"
    lines = [
        "# Retrieval Context",
        "",
        f"- query: {args.query}",
        f"- generated_at: {now_iso()}",
        f"- top_k: {top_k}",
        "",
        "## Results",
        "",
    ]
    for idx, row in enumerate(results, start=1):
        lines.extend(
            [
                f"### [{idx}] {row['title']}",
                "",
                f"- path: `{row['path']}`",
                f"- heading: {row['heading']}",
                f"- score: {row['score']}",
                "",
                "```text",
                row["text"].strip(),
                "```",
                "",
            ]
        )
    if not results:
        lines.append("No retrieval results. The writer must ask for more material or broaden the query.")
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {rel(out_path)}")
    return 0


def classify(text: str, path: Path, config: dict) -> tuple[str, list[str]]:
    sample = f"{path.name}\n{text[:6000]}".lower()
    best_name = "general"
    best_tags = ["domain/general"]
    best_score = 0
    for item in config.get("classification", []):
        score = sum(1 for kw in item.get("keywords", []) if kw.lower() in sample)
        if score > best_score:
            best_name = item["name"]
            best_tags = item.get("tags", [])
            best_score = score
    return best_name, best_tags


def existing_material_ids(config: dict) -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / config["paths"]["sources"]).rglob("*.md"):
        fm = parse_frontmatter(read_text_lossy(path))
        material_id = str(fm.get("material_id", "")).strip()
        if material_id:
            ids.add(material_id)
    return ids


def source_card_text(path: Path, material_id: str, text: str, extractor: str, domain: str, tags: list[str]) -> str:
    created = today()
    title = path.stem.strip() or path.name
    tag_lines = "\n".join(f"  - {tag}" for tag in ["source", "inbox", *tags])
    sample = text.strip()
    if len(sample) > 1800:
        sample = sample[:1800].rstrip() + "\n..."
    if not sample:
        sample = "未能自动提取文本。请人工补充摘要，或安装/配置对应的本地解析工具。"
    return f"""---
type: source
status: inbox
created: {created}
updated: {created}
material_id: "{material_id}"
source_path: "{rel(path)}"
source_ext: "{path.suffix.lower()}"
extractor: "{extractor}"
suggested_domain: "{domain}"
tags:
{tag_lines}
aliases: []
---
# {title}

## 摘要

待整理。

## 核心要点

- 待整理。

## 可复用材料

- 待整理。

## 原文摘录

```text
{sample}
```

## 关联笔记

## 处理记录

- {created}: harness ingest created this source card from `{rel(path)}`.
"""


def cmd_ingest(args: argparse.Namespace) -> int:
    config = load_config()
    ensure_dirs(config)
    inbox = ROOT / config["paths"]["inbox_materials"]
    sources = ROOT / config["paths"]["sources"]
    known_ids = existing_material_ids(config)
    created = 0
    skipped = 0
    unsupported = 0
    for path in sorted(p for p in inbox.rglob("*") if p.is_file() and not p.name.startswith(".")):
        digest = sha256_file(path)
        material_id = f"sha256:{digest}"
        if material_id in known_ids:
            skipped += 1
            continue
        text, extractor = extract_text(path)
        if extractor == "unsupported":
            unsupported += 1
        domain, tags = classify(text, path, config)
        slug = safe_slug(path.stem, "material")
        card_path = sources / f"{slug}-{digest[:8]}.md"
        if args.dry_run:
            print(f"Would create {rel(card_path)} from {rel(path)} [{extractor}, {domain}]")
            continue
        card_path.write_text(source_card_text(path, material_id, text, extractor, domain, tags), encoding="utf-8")
        known_ids.add(material_id)
        created += 1
        print(f"Created {rel(card_path)}")
    print(f"Ingest complete: created={created}, skipped={skipped}, unsupported={unsupported}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    config = load_config()
    ensure_dirs(config)
    print("Vault directories are ready.")
    return 0


def all_markdown_files() -> list[Path]:
    ignored = {".obsidian", ".git", "90_System/index", "90_System/context"}
    files = []
    for path in ROOT.rglob("*.md"):
        rel_path = rel(path)
        if any(rel_path == item or rel_path.startswith(item + "/") for item in ignored):
            continue
        files.append(path)
    return sorted(files)


def check_broken_links(files: list[Path]) -> list[str]:
    known_names = {path.stem for path in files}
    known_rel_no_ext = {rel(path)[:-3] for path in files if path.suffix == ".md"}
    problems: list[str] = []
    for path in files:
        text = read_text_lossy(path)
        for match in WIKILINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or "." in Path(target).suffix:
                continue
            if target not in known_names and target not in known_rel_no_ext:
                problems.append(f"Broken wikilink in {rel(path)} -> [[{target}]]")
    return problems


def check_frontmatter(files: list[Path]) -> list[str]:
    problems: list[str] = []
    required_dirs = ("01_Sources/", "02_Notes/", "03_Projects/", "04_Outputs/")
    for path in files:
        rel_path = rel(path)
        if rel_path.startswith("90_System/templates/") or rel_path.startswith("90_System/prompts/"):
            continue
        if rel_path.startswith(required_dirs):
            fm = parse_frontmatter(read_text_lossy(path))
            for key in ("type", "status", "created", "updated", "tags"):
                if key not in fm:
                    problems.append(f"Missing `{key}` in {rel_path}")
    return problems


def check_index_freshness(config: dict) -> list[str]:
    index_path = ROOT / config["paths"]["index"] / "wiki_index.jsonl"
    if not index_path.exists():
        return ["Index missing. Run `python3 harness/wiki.py build-index`."]
    index_mtime = index_path.stat().st_mtime
    stale = [path for path in note_paths(config) if path.stat().st_mtime > index_mtime]
    if stale:
        return [f"Index stale: {len(stale)} note(s) changed after last build-index."]
    return []


def cmd_doctor(args: argparse.Namespace) -> int:
    config = load_config()
    ensure_dirs(config)
    files = all_markdown_files()
    problems = []
    problems.extend(check_frontmatter(files))
    problems.extend(check_broken_links(files))
    problems.extend(check_index_freshness(config))
    if problems:
        print("Doctor found issues:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(f"Doctor OK. Checked {len(files)} markdown files.")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    config = load_config()
    rows = load_index(config)
    eval_path = ROOT / config["paths"]["evals"] / "retrieval_cases.jsonl"
    if not eval_path.exists():
        print(f"No eval file: {rel(eval_path)}")
        return 0
    cases = []
    with eval_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    if not cases:
        print("No eval cases.")
        return 0
    top_k = args.top_k or int(config["index"]["top_k"])
    passed = 0
    for case in cases:
        results = search_rows(rows, case["query"], top_k)
        paths = [item["path"] for item in results]
        must = case.get("must_include", [])
        matched = [req for req in must if any(req in path for path in paths)]
        hit = len(matched) == len(must)
        status = "PASS" if hit else "FAIL"
        passed += int(hit)
        print(f"{status}: {case['query']}")
        print(f"  expected all: {must}")
        print(f"  got: {paths[:5]}")
    print(f"Eval: {passed}/{len(cases)} passed @ top_k={top_k}")
    return 0 if passed == len(cases) else 1


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="wikiR local harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create required directories").set_defaults(func=cmd_init)
    sub.add_parser("build-index", help="build local lexical index").set_defaults(func=build_index)

    ingest = sub.add_parser("ingest", help="create source cards from 00_Inbox/materials")
    ingest.add_argument("--dry-run", action="store_true")
    ingest.set_defaults(func=cmd_ingest)

    search = sub.add_parser("search", help="search indexed wiki chunks")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=0)
    search.set_defaults(func=cmd_search)

    context = sub.add_parser("context", help="write retrieval context for local LLM")
    context.add_argument("query")
    context.add_argument("--top-k", type=int, default=0)
    context.set_defaults(func=cmd_context)

    sub.add_parser("doctor", help="validate vault structure").set_defaults(func=cmd_doctor)

    eval_parser = sub.add_parser("eval", help="run retrieval eval cases")
    eval_parser.add_argument("--top-k", type=int, default=0)
    eval_parser.set_defaults(func=cmd_eval)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
