#!/bin/bash
# build_slides.sh — Marp-cli wrapper for Educational Material Maker
#
# Usage:
#   ./scripts/build_slides.sh <slides.md>                          → outputs slides.html (edu-default theme)
#   ./scripts/build_slides.sh <slides.md> --pdf                    → outputs slides.pdf
#   ./scripts/build_slides.sh <slides.md> --theme edu-warm         → use edu-warm theme
#   ./scripts/build_slides.sh <slides.md> --no-theme               → outputs without custom theme
#
# Available themes: edu-default, edu-warm, edu-dark, edu-stem, edu-humanities, edu-minimal
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
THEME_NAME="edu-default"
SKIP_THEME=""
OUTPUT="${INPUT%.md}.html"

while [ $# -gt 0 ]; do
    case "$1" in
        --pdf) PDF_FLAG="--pdf"; OUTPUT="${INPUT%.md}.pdf" ;;
        --no-theme) SKIP_THEME="1" ;;
        --theme) shift; THEME_NAME="$1" ;;
        --theme=*) THEME_NAME="${1#--theme=}" ;;
    esac
    shift
done

# Resolve theme CSS file
THEME_CSS="$PLUGIN_ROOT/themes/${THEME_NAME}.css"
THEME_FLAG=""
if [ -z "$SKIP_THEME" ] && [ -f "$THEME_CSS" ]; then
    # Load ALL theme files so @import chains work
    ALL_THEMES=$(ls "$PLUGIN_ROOT/themes/"*.css 2>/dev/null | tr '\n' ' ')
    THEME_FLAG="--theme-set $ALL_THEMES --theme $THEME_NAME"
    echo "Theme: $THEME_NAME"
elif [ -z "$SKIP_THEME" ]; then
    echo "Warning: theme '$THEME_NAME' not found at $THEME_CSS, using default marp theme" >&2
fi

echo "Building: $INPUT → $OUTPUT"
npx @marp-team/marp-cli "$INPUT" $THEME_FLAG $PDF_FLAG -o "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "Done: $OUTPUT"
else
    echo "Error: output file not created" >&2
    exit 1
fi
