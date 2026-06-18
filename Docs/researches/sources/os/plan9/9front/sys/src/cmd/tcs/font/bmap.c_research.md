# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/bmap.c

Maps Unicode Rune ranges to Big5 table ordinals for font generation.

Key points:
- Initializes the `chars` output range to zero.
- Scans `tabbig5[0..BIG5MAX)` and records the Big5 ordinal for each Rune in the requested inclusive range.
- Counts missing Runes and prints a diagnostic with the number found and one missing example.
- The failure exit is commented out, so missing glyphs are tolerated.

Dependencies and interactions:
- Includes `../big5.h`.
- Used by `font/main.c` for Big5 font extraction before calling `breadbits`.

Research relevance:
- Small reverse-mapping helper connecting Big5 conversion data to font extraction.
