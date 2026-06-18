# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gmap.c

Maps requested rune range to GB glyph ordinals.

Key function:
- `gmap(from, to, chars)` scans `tabgb` and stores each matching table index in `chars[rune-from]`.

Notable behavior:
- Missing requested runes are reported but not fatal.
- Mirrors `bmap` and `kmap` structure.
