#!/usr/bin/env bash
# Delega para install_linux.sh na raiz do repositório (ver INSTALL_LINUX.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/install_linux.sh" "$@"
