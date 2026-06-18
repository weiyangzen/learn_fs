# File Research: sources/os/plan9/plan9/sys/src/cmd/tr.c

Unicode-aware Plan 9 `tr` implementation.

Key responsibilities:
- Parses `-c`, `-d`, and `-s`.
- Parses rune specifications, escapes, hex escapes, octal escapes, and ranges.
- Implements deletion, squeezing, transliteration, and complement transliteration.
- Uses bitsets sized for `Runemax+1`.
- Reads and writes UTF-8 runes with buffering.

Important behavior:
- Ranges are expanded by `canon()` using parser state.
- Repeated destination exhaustion uses the last destination rune.
- `-s` squeezes runs of output runes found in the destination set.
- `-c` builds a complement mapping up to the highest rune seen in either specification.

Notable risks:
- Complement transliteration maps runes above the computed high-water mark to the last destination rune.
- Large ranges can allocate large mapping arrays.
- Ambiguous repeated source mappings in transliteration are rejected.
