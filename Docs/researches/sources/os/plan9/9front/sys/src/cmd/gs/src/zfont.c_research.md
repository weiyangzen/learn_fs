# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont.c

## Purpose
Implements generic PostScript font operators, global font-directory initialization, transformed font dictionary creation, font cache parameters, font restore cleanup, and Unicode decoder setup.

## Key Functions
- `zfont_init()` allocates `ifont_dir`, installs glyph marking/global glyph lookup callbacks, and registers it as a GC root.
- `zscalefont()`, `zmakefont()`, and `make_font()` create transformed fonts.
- `zsetfont()` and `zcurrentfont()` update/query the current graphics-state font.
- `zcachestatus()`, `zsetcachelimit()`, `zsetcacheparams()`, and `zcurrentcacheparams()` expose font/character cache controls.
- `zregisterfont()` marks a font as a resource.
- `font_param()` validates a PostScript font dictionary and extracts its `gs_font`.
- `add_FID()` installs the font identifier in a dictionary.
- `zbase_make_font()` and `zdefault_make_font()` build transformed font dictionaries with `FontMatrix`, `OrigFont`, `ScaleMatrix`, and new `FID`.
- `font_restore()` purges fonts/cache entries invalidated by VM restore.
- `zfont_info()` fills font-info strings from `FontInfo`.
- `setup_unicode_decoder()` stores a glyph-to-Unicode decoding dictionary in the font directory.

## Important Behavior
- `font_param()` checks that `FID` points back to the same dictionary, preventing mismatched font ids.
- `make_font()` temporarily substitutes the caller's dictionary so changed encodings can affect transformed fonts.
- Restore cleanup purges original fonts, scaled fonts, xfonts, and cached characters whose glyph names were allocated after the save.
- Unicode decoder storage has custom GC enumeration/relocation.

## Research Notes
This file is the common font operator layer used by all font-type-specific builders in adjacent files.
