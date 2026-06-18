# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/kbits.c

Reads JIS/kuten hex bitmap files and builds a packed Plan 9 `Bitmap`.

Key points:
- `kreadbits` opens a text bitmap source, allocates a `done` array, and computes min/max requested ordinals.
- Skips two header lines before reading glyph rows.
- Parses each line's character ordinal with `strtol(p + 17, ...)`.
- For matching requested ordinals, decodes hex bitmap bytes from `p + 25` into the interleaved `bits` buffer.
- Compacts present glyphs into `nbits`, allocates a `Bitmap` of width `nch * size` and height `size`, and writes bitmap data.
- Like `gbits.c`, reuses loop variable `i` inside the glyph-copy row loop, relying on an immediate break after a match.

Dependencies and interactions:
- Called by `font/main.c` for JIS source data.
- Usually paired with `kmap`, which maps Unicode ranges to JIS X 0208/kuten ordinals.

Research relevance:
- JIS bitmap reader for building Plan 9 Han subfonts.
