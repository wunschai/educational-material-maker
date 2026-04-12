#!/bin/bash
# build_slides.sh — Marp-cli wrapper for Educational Material Maker
#
# Usage:
#   ./scripts/build_slides.sh <slides.md>         → outputs slides.html
#   ./scripts/build_slides.sh <slides.md> --pdf    → outputs slides.pdf
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

# Determine output format
PDF_FLAG=""
OUTPUT="${INPUT%.md}.html"
for arg in "$@"; do
    if [ "$arg" = "--pdf" ]; then
        PDF_FLAG="--pdf"
        OUTPUT="${INPUT%.md}.pdf"
    fi
done

echo "Building: $INPUT → $OUTPUT"
npx @marp-team/marp-cli "$INPUT" $PDF_FLAG -o "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "Done: $OUTPUT"
else
    echo "Error: output file not created" >&2
    exit 1
fi
