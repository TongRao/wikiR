#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))

import wiki  # noqa: E402


def argv_for_tool(tool: str, args: dict) -> list[str]:
    if tool == "wiki_init":
        return ["init"]
    if tool == "wiki_ingest":
        argv = ["ingest"]
        if args.get("dry_run"):
            argv.append("--dry-run")
        return argv
    if tool == "wiki_build_index":
        return ["build-index"]
    if tool == "wiki_search":
        query = args.get("query")
        if not query:
            raise ValueError("wiki_search requires args.query")
        argv = ["search", str(query)]
        if args.get("top_k"):
            argv.extend(["--top-k", str(args["top_k"])])
        return argv
    if tool == "wiki_context":
        query = args.get("query")
        if not query:
            raise ValueError("wiki_context requires args.query")
        argv = ["context", str(query)]
        if args.get("top_k"):
            argv.extend(["--top-k", str(args["top_k"])])
        return argv
    if tool == "wiki_doctor":
        return ["doctor"]
    if tool == "wiki_eval":
        argv = ["eval"]
        if args.get("top_k"):
            argv.extend(["--top-k", str(args["top_k"])])
        return argv
    raise ValueError(f"Unknown wikiR tool: {tool}")


def run_request(request: dict) -> dict:
    tool = request.get("tool")
    args = request.get("args") or {}
    if not isinstance(args, dict):
        raise ValueError("request.args must be an object")
    if not tool:
        raise ValueError("request.tool is required")

    argv = argv_for_tool(str(tool), args)
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = 0
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            exit_code = int(wiki.main(argv))
        except SystemExit as exc:
            exit_code = int(exc.code or 0)

    return {
        "ok": exit_code == 0,
        "tool": tool,
        "exit_code": exit_code,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
    }


def load_request() -> dict:
    if len(sys.argv) > 1:
        return json.loads(sys.argv[1])
    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("Expected JSON request on stdin or argv[1]")
    return json.loads(raw)


def main() -> int:
    try:
        response = run_request(load_request())
    except Exception as exc:
        response = {
            "ok": False,
            "tool": None,
            "exit_code": 2,
            "stdout": "",
            "stderr": str(exc),
        }
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
