#!/bin/bash
# build_slides.sh — Marp-cli wrapper for Educational Material Maker
#
# Usage:
#   ./scripts/build_slides.sh <slides.md>         → outputs slides.html (with edu-default theme)
#   ./scripts/build_slides.sh <slides.md> --pdf    → outputs slides.pdf
#   ./scripts/build_slides.sh <slides.md> --no-theme → outputs without custom theme
#
# Dependencies: Node.js + npx (marp-cli installed on-demand via npx)
# Exit codes: 0 success, 1 error

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <slides.md> [--pdf]" >&2
    exit 1
fi

INPUT="$1"
shift

if [ ! -f "$INPUT" ]; then
    echo "Error: file not found: $INPUT" >&2
    exit 1
fi

# Check npx availability
if ! command -v npx &> /dev/null; then
    echo "Error: npx not found. Please install Node.js and npm." >&2
    exit 1
fi

# Resolve plugin root (for theme path)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
THEME_PATH="$PLUGIN_ROOT/themes/edu-default.css"

# Parse flags
PDF_FLAG=""
THEME_FLAG=""
OUTPUT="${INPUT%.md}.html"
for arg in "$@"; do
    if [ "$arg" = "--pdf" ]; then
        PDF_FLAG="--pdf"
        OUTPUT="${INPUT%.md}.pdf"
    elif [ "$arg" = "--no-theme" ]; then
        THEME_FLAG="skip"
    fi
done

# Auto-apply edu-default theme if available and not skipped
if [ "$THEME_FLAG" != "skip" ] && [ -f "$THEME_PATH" ]; then
    THEME_FLAG="--theme-set $THEME_PATH --theme edu-default"
    echo "Theme: edu-default"
fi

echo "Building: $INPUT → $OUTPUT"
npx @marp-team/marp-cli "$INPUT" $THEME_FLAG $PDF_FLAG -o "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "Done: $OUTPUT"
else
    echo "Error: output file not created" >&2
    exit 1
fi
