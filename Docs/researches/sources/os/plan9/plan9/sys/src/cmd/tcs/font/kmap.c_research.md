# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kmap.c

Maps requested rune range to Kuten/JIS glyph ordinals.

Key function:
- `kmap(from, to, chars)` scans `tabkuten208` and stores the Kuten table index for each rune in range.

Notable behavior:
- Reports but does not abort on missing mappings.
- Does not treat negative ambiguous mapping entries specially; it only matches entries whose stored value is within the requested positive rune range.
