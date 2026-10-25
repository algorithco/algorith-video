#!/usr/bin/env bash
# Cross-platform exporter; artwork is supplied by Algorithco.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"${PYTHON:-python3}" "$ROOT/scripts/icon/export-assets.py"
