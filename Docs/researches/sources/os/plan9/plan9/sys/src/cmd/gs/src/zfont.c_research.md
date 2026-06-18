# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfont.c

## Purpose
Implements generic PostScript font operators, global font-directory initialization, transformed font dictionary creation, font cache parameters, restore cleanup, and Unicode decoder setup.

## Key Functions
- `zfont_init()` allocates `ifont_dir` and registers it as a GC root.
- `zscalefont()`, `zmakefont()`, and `make_font()` create transformed fonts.
- `zsetfont()` and `zcurrentfont()` update/query the graphics-state font.
- Cache operators expose font/character cache controls.
- `font_param()` validates a PostScript font dictionary and extracts its `gs_font`.
- `zdefault_make_font()` builds transformed font dictionaries with `FontMatrix`, `OrigFont`, `ScaleMatrix`, and new `FID`.
- `font_restore()` purges fonts/cache entries invalidated by VM restore.
- `setup_unicode_decoder()` stores a glyph-to-Unicode decoding dictionary.

## Important Behavior
- `font_param()` checks that `FID` points back to the same dictionary.
- `make_font()` temporarily substitutes the caller's dictionary so changed encodings can affect transformed fonts.
- Restore cleanup purges fonts, xfonts, and cached characters whose glyph names were allocated after the save.

## Research Notes
Common font operator layer used by all font-type-specific builders.
