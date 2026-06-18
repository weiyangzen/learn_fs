# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/htroff.c

Purpose: Parses troff device-independent output and renders pages into a Plan 9 draw window for preview.

Key behavior:
- Maintains device resolution, current position, scaling divisor, offsets, page views, page index, font, and size state.
- `readpage` interprets troff commands: page starts, characters, special characters, numeric glyphs, drawing commands, size/font changes, motion, comments, lines, and device controls.
- Drawing supports lines, circles, ellipses, arcs, and splines/wiggly lines.
- `devcntrl` handles resolution, device name, and font mounting.
- `skipto` uses buffered input offsets and page index to navigate pages.
- `botpage` handles interactive commands for quit, repaint, magnification, offsets, multi-view layout, page numbers, relative motion, and debug toggle.
- `eresized` refreshes layout on window resize.

Dependencies and integration:
- Uses `proof/main.c` ring-buffer input functions, `screen.c` command input, and `font.c` glyph rendering.

Risks and notes:
- Must parse skipped pages to discover font loads.
- Page offset buffer is bounded by `NPAGENUMS`.
- Some troff device controls are ignored.
