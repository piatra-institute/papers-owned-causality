#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Note: monofont set to Menlo (ships with macOS, full Unicode coverage).
# Linux users without Menlo can substitute "DejaVu Sans Mono".
pandoc PAPER.md \
    -o PAPER.pdf \
    --pdf-engine=xelatex \
    --resource-path=. \
    -H scripts/preamble.tex \
    -V mainfont="Palatino" \
    -V mathfont="Palatino" \
    -V monofont="Menlo" \
    -V fontsize=11pt \
    -V geometry:"margin=1in" \
    -V linestretch=1.15

echo "PAPER.pdf"
