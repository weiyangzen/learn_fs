# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.c

Large static Big5-to-rune mapping table.

Contents:
- Defines `long tabbig5[BIG5MAX]`.
- Indexed by Big5 ordinal computed by `conv_big5.c`.
- Entries are Unicode/Plan 9 rune values or `-1` for unmapped holes.
- Includes punctuation, symbols, fullwidth Latin, Greek, kana, Cyrillic, CJK ideographs, compatibility code points, and large undefined regions.

Dependencies:
- Includes `big5.h`, which defines `BIG5MAX = 13973`.

Role:
- Primary forward mapping for Big5 input.
- Also used to build reverse rune-to-Big5 map in `big5_out`.
- Used by `tcs/font/bmap.c` to locate Big5 glyph indices for requested runes.
