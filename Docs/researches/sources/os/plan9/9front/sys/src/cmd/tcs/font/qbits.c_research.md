# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/qbits.c

Reads GB quwei-encoded bitmap text data and builds a packed Plan 9 `Bitmap`.

Key points:
- Comment identifies input as quwei encoding for GB.
- `qreadbits` opens a source file, allocates a `done` array, and computes min/max requested ordinals.
- Parses each line's first four decimal digits as the quwei code.
- For requested codes, decodes hex bitmap rows starting at `p + 5` into the caller-provided interleaved bitmap buffer.
- Compacts present glyphs into `nbits`, allocates a packed `Bitmap`, and writes it with `wrbitmap`.
- Same variable-reuse fragility as `kbits.c`/`gbits.c`: `i` is reused for row iteration inside the character-search loop and then immediately breaks.

Dependencies and interactions:
- Used by `font/main.c` in `Gb_qw` mode, usually after `gmap` maps Unicode to GB ordinals.

Research relevance:
- Alternate GB bitmap reader for quwei text sources.
