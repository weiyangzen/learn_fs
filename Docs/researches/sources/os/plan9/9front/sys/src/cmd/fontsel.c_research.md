# File Research: sources/os/plan9/9front/sys/src/cmd/fontsel.c

## Purpose
Graphical font selector and preview tool.

## Key Elements
Scans `/lib/font/bit` and `/lib/font/ttf`, builds sorted font directories and face lists, previews default multilingual and code sample text or user-provided text, uses button menus to select font families/faces, uses `+`/`-` to change size or face index, redraws on resize, and prints the selected font path on exit.

## Dependencies
Uses Plan 9 draw/thread/mouse/keyboard menu APIs, bitmap fonts, and mounted TTF font paths under `/n/ttf`.

## Behavior/Risks
TTF handling assumes the external `/n/ttf/name.size/font` namespace exists. Text input is capped at 256 lines. Some key handling reuses `ifont` as TTF size through a union field.
