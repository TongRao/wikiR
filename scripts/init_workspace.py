#!/usr/bin/env python3
"""Initialize the wikiR workspace structure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "08_MCP"))

from tools.paths import init_workspace_files  # noqa: E402


def main() -> int:
    """Create required directories and base files."""
    parser = argparse.ArgumentParser(description="Initialize wikiR workspace")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite managed base files")
    args = parser.parse_args()
    result = init_workspace_files(overwrite=args.overwrite)
    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

