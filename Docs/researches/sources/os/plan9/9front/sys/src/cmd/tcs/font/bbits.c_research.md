# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/bbits.c

Reads Big5 bitmap font data and builds a packed Plan 9 `Bitmap`.

Key points:
- Defines Big5 font layout constants `Charsperfont`, `Void1b`, and `Void1e`.
- `breadbits` opens a bitmap source file, allocates a per-character `done` array, and extracts glyph bitmaps for requested Big5 ordinals.
- Skips a known void range and compares glyph data against a static 32-byte `missing` pattern.
- Computes source offsets with Plan 9-specific font-layout adjustments, including a 256-byte header and a documented hole between Big5 ranges.
- Writes requested glyph rows into a wide temporary `bits` buffer, then compacts only present glyphs into `nbits`.
- Allocates a destination `Bitmap` of width `nch * size` and height `size`, writes bitmap data with `wrbitmap`, and returns it.

Dependencies and interactions:
- Called through the `readbitsfn` table in `font/main.c` when source type is Big5.
- Consumes character ordinals produced by `bmap`.

Research relevance:
- Font-build helper for deriving Plan 9 subfonts from Big5 bitmap data.
