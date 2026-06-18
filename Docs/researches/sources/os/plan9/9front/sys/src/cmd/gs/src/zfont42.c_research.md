# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont42.c

## Purpose
Builds Type 42 TrueType fonts and provides shared TrueType access helpers for CIDFontType 2.

## Key Functions
- `build_gs_TrueType_font()` validates `sfnts` and `GlyphDirectory`, builds a primitive Type 42/Type 11 font, initializes TrueType data, and installs glyph access procedures.
- `zbuildfont42()` defines a regular Type 42 font.
- `font_string_array_param()` validates string-array parameters such as `sfnts` and `CIDMap`.
- `font_GlyphDirectory_param()` accepts dictionary/array glyph directories or null.
- `string_array_access_proc()` accesses a byte span across an array of strings, ignoring sfnts odd-length padding when requested.
- `glyph_to_index()` maps glyph names through `CharStrings` to GID glyphs.
- `font_gdir_get_outline()` and `z42_gdir_get_outline()` get glyph data from `GlyphDirectory`.
- `z42_enumerate_glyph()` and `z42_gdir_enumerate_glyph()` enumerate glyph names or indexes.
- `z42_encode_char()`, `z42_glyph_outline()`, and `z42_glyph_info()` accept either glyph names or glyph indexes.
- `z42_string_proc()` reads bytes from the `sfnts` array.

## Important Behavior
- `sfnts` is checked immediately by reading the first array element as a string.
- If `GlyphDirectory` is present, it replaces `loca`/`glyf` outline access and glyph enumeration.
- Missing glyph-directory outlines return null glyph data rather than immediate failure.
- GID glyphs are represented with `GS_MIN_GLYPH_INDEX` offset.

## Research Notes
This file is the main bridge between PostScript Type 42 dictionaries and the graphics library's TrueType engine; `zfcid1.c` reuses it for CID-keyed TrueType.
