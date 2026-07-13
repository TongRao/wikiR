#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
SERVER_PATH="$ROOT_DIR/08_MCP/material_mcp_server.py"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "[wikiR MCP] Missing virtual environment: $ROOT_DIR/.venv" >&2
  echo "[wikiR MCP] Create it first:" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install -r 08_MCP/requirements.txt" >&2
  exit 1
fi

cd "$ROOT_DIR"
echo "[wikiR MCP] Starting server" >&2
echo "[wikiR MCP] workspace: $ROOT_DIR" >&2
echo "[wikiR MCP] server: $SERVER_PATH" >&2
echo "[wikiR MCP] transport: stdio" >&2
echo "[wikiR MCP] Ready for Hermes MCP connection. No further console output means the stdio server is waiting for MCP messages." >&2
exec "$PYTHON_BIN" "$SERVER_PATH"
