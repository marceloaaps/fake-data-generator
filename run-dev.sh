#!/usr/bin/env bash
# Roda o app com o venv da raiz do projeto (evita confusão com source/.venv).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/.venv/bin/python" "$ROOT/source/main.py" "$@"
