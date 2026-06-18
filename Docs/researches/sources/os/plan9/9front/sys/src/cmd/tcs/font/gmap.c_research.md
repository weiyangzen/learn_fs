# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/gmap.c

Maps Unicode Rune ranges to GB2312 ordinals for font generation.

Key points:
- Initializes all requested `chars` entries to zero.
- Scans `tabgb[0..GBMAX)` and records the GB ordinal for every Rune in the requested range.
- Reports how many requested Runes were found and gives one missing example when there are gaps.
- Does not abort on missing mappings because the exit call is commented out.

Dependencies and interactions:
- Includes `../gb.h`.
- Used by `font/main.c` for both BDF and quwei GB font readers.

Research relevance:
- Reverse lookup bridge from Unicode ranges to GB font source encodings.
