# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/gbits.c

Reads BDF font files for GB glyphs and builds a packed Plan 9 `Bitmap`.

Key points:
- Comment notes that BDF `ENCODING` is font dependent.
- `greadbits` opens a BDF file, allocates a `done` array, and determines the min/max requested character ordinal.
- Scans BDF `STARTCHAR` blocks, reads `ENCODING`, converts it to the GB ordinal `(high - 0xA0) * 100 + (low - 0xA0)`, and reads `BITMAP` hex rows.
- Decodes hex bitmap rows through a local nibble table.
- Copies only requested glyphs into the caller-provided row-major `bits` buffer and marks them done.
- Compacts present glyphs into `nbits`, allocates a packed `Bitmap`, and writes it with `wrbitmap`.
- Helper `field` scans for required BDF fields and exits on malformed or incomplete glyph records.
- The inner glyph-copy loop reuses variable `i` for row iteration inside a loop already using `i` for character lookup; the function breaks immediately after copying, so it works but is fragile.

Dependencies and interactions:
- Called through `font/main.c` for `Gb_bdf`.
- Consumes ordinals produced by `gmap`.

Research relevance:
- BDF-to-Plan-9-bitmap converter for GB subfont generation.
