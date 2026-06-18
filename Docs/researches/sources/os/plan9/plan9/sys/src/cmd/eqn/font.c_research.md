# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/font.c

Font state handling for `eqn`.

Key behavior:
- `setfont()` maps R/I/B and named fonts into troff font identifiers and pushes current font state.
- `font()` applies a font change to an equation box and restores the prior font.
- `globfont()` changes global default font.
- `fatbox()` simulates bold/fat text by overprinting a shifted copy.

Filesystem relevance:
- Typesetting state only.
