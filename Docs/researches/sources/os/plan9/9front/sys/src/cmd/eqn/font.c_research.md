# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/font.c

This file manages local and global font changes in eqn and implements “fat” rendering.

Key responsibilities:
- `setfont` interprets font names/aliases (`I`, `B`, `R`) and pushes a new font stack entry.
- `font` applies a font to a parsed box and restores the previous font.
- `globfont` sets the default font from input.
- `fatbox` overlays a box on itself with a small horizontal shift to simulate bold/fattened output.

Important implementation notes:
- Italic and bold are mapped to troff font positions 2 and 3.
- Unknown font names are treated as roman-style named fonts.
- Font stack overflow is fatal at depth 10.
- Box font metadata is simplified: non-italic renderings are generally marked roman.
