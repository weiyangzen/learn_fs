# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/font.c

Builds a Plan 9 `Subfont` descriptor from a generated glyph bitmap.

Key function:
- `bf(n, size, b, done)` allocates `Fontchar[n+1]`, creates per-character metrics, skips missing glyphs by assigning width `0`, and calls `subfalloc`.

Metrics:
- Each present glyph is `size` pixels wide and high.
- Ascent is `size*7/8`.
- `x` positions advance only for found glyphs.

Dependencies:
- Plan 9 graphics types `Bitmap`, `Subfont`, `Fontchar`.
