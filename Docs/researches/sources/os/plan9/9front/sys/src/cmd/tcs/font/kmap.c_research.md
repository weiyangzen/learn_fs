# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/kmap.c

Maps Unicode Rune ranges to JIS X 0208/kuten ordinals for font generation.

Key points:
- Initializes requested `chars` entries to zero.
- Scans `tabkuten208[0..KUTEN208MAX)` and records the kuten ordinal for Runes in the requested range.
- Reports the count of found/missing characters and one missing example when mappings are incomplete.
- Does not abort on missing mappings because the exit call is commented out.

Dependencies and interactions:
- Includes `../kuten208.h`.
- Used by `font/main.c` for JIS font extraction.

Research relevance:
- Reverse mapping from Unicode ranges to JIS/kuten source glyph positions.
