#!/usr/bin/env bash
# Offline code/document checks. This is not a GPU training setup.
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_PYTHON="${PYTHON_BIN:-python3}"
cd -- "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

"$PROJECT_PYTHON" --version
"$PROJECT_PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Python 3.10 or newer is required; set PYTHON_BIN to a compatible interpreter")'
"$PROJECT_PYTHON" scripts/check_environment.py
"$PROJECT_PYTHON" -m compileall -q src scripts
"$PROJECT_PYTHON" -m unittest discover -s tests -v
"$PROJECT_PYTHON" scripts/check_project.py

