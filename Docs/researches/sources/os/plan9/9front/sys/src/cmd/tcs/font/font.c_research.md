# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/font.c

Builds a Plan 9 `Subfont` descriptor from a bitmap and glyph-presence array.

Key points:
- `bf` allocates `Fontchar` metadata for `n + 1` entries.
- For each character, sets fixed-size metrics `{x, 0, size, 0, size}`.
- Advances the packed bitmap x-offset only when `done[i]` is true; missing glyphs get zero width.
- Creates a `Subfont` with `subfalloc`, using height `size` and ascent `size * 7 / 8`.

Dependencies and interactions:
- Called by `font/main.c` after a bitmap reader returns its packed bitmap and `found` array.

Research relevance:
- Converts extracted bitmap glyph data into a serializable Plan 9 subfont.
