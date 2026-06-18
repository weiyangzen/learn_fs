# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/tune.c

Tamil TUNE encoding converter for `tcs`.

Key responsibilities:
- Defines mapping tables from Unicode Tamil vowels, consonants, virama/vowel marks, and special forms to TUNE private-use code points.
- Provides lookup helpers for TUNE-to-Unicode, Unicode-to-TUNE, and mark-index lookup.
- `tune_in()` reads UTF runes with `Bgetrune`, converts TUNE private-use glyphs into Unicode Tamil sequences, and passes output to the selected converter.
- `tune_out()` is a state machine that combines Tamil base characters and following marks into TUNE glyphs.

Important behavior:
- Handles special Tamil ligature-like sequences such as ksha and shri.
- Handles composite vowel signs by delaying emission until enough context is seen.
- Leaves non-TUNE runes unchanged, except unknown TUNE private-use code points are diagnosed or cleaned.

Notable risks:
- `tune_out()` preserves state across calls and must receive a zero-length flush to emit a pending glyph.
- It uses fixed `obuf` inherited from the `tcs` core; output expansion depends on the shared batch size.
- Many mappings are encoded as literal private-use values, so behavior is table-sensitive and hard to infer without the font/encoding convention.
