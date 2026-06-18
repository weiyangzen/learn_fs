# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gb.c

Defines the GB2312-to-Unicode mapping table used by `tcs`.

Key points:
- Includes `gb.h` and defines `long tabgb[GBMAX]`.
- `GBMAX` is 8795, and the file contains exactly 8795 table entries.
- Mapping ordinals correspond to the header's kuten-like GB range representation, with many unused positions represented as `-1`.
- Reading/counting found 7445 mapped entries and 1350 `-1` entries.
- Early mapped entries include CJK punctuation, fullwidth forms, symbols, Hiragana, Katakana, Greek, Cyrillic, pinyin letters, Bopomofo, and box-drawing characters.
- The bulk of the table maps GB2312 Hanzi ordinals to Unicode CJK code points.
- Dense Unicode blocks in the table include `U+30xx`, `U+4Exx`, `U+54xx`, `U+62xx`, `U+6Cxx`, `U+95xx`, `U+53xx`, `U+82xx`, `U+8Dxx`, and `U+80xx`.

Dependencies and interactions:
- Used by `conv_gb.c` for decoding GB byte pairs and by `gb_out` reverse mapping.
- Used by `font/gmap.c` to map Unicode ranges to GB font ordinals.

Research relevance:
- Static mapping data that makes GB2312 conversion and GB font lookup possible.
