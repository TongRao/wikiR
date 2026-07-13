#!/usr/bin/env python3
"""Manual CLI for testing inbox processing without Hermes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_MCP"))

from tools.inbox_process import process_inbox  # noqa: E402
from tools.paths import init_workspace_files  # noqa: E402


def main() -> int:
    """Run inbox processing and print a JSON result."""
    parser = argparse.ArgumentParser(description="Process wikiR inbox files")
    parser.add_argument("--mode", default="fast", choices=["fast", "accurate"])
    args = parser.parse_args()

    init_workspace_files(overwrite=False)
    result = process_inbox(mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"ok", "partial_error"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

