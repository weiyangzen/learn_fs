# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.h

Purpose: Shared declarations, types, globals, constants, and prototypes for `tr2post`.

Key contents:
- Constants for special characters, token sizes, and charlib path.
- Externs for debug, font size/position, device state, font tables, current troff font, drawing flag, build-char list.
- `specname`, `charent`, `pfnament`, `psfent`, and `troffont` structures.
- Prototypes for initialization, font mounting/resolution, glyph output, conversion, motion, drawing, device control, errors, page/string state, font selection, DESC parsing, picture/path inclusion, and PostScript inclusion.

Dependencies and integration:
- Included by nearly every `tr2post` source file.
- Ties together `common.h` constants such as `NUMOFONTS` and `FONTSIZE`.

Risks and notes:
- Heavy reliance on global mutable state.
- Function declarations use legacy C style in places.
