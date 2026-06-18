# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont42.h

Defines Type 42 TrueType font internal data structures and public helpers.

Key definitions:
- `gs_type42_mtx_t` describes hmtx/vmtx table count, offset, and length.
- `gs_type42_data` stores client-provided string access/proc data, initialized glyph index/outline/metrics callbacks, cached table offsets, unitsPerEm, indexToLocFormat, metrics tables, glyph counts, loca-derived lengths, glyph cache, and warning flags.
- `gs_font_type42_common` extends base font fields with Type 42 data.
- `gs_font_type42` is the concrete Type 42 font object.
- Declares GC metadata for Type 42 fonts.

Key declarations:
- `gs_type42_font_init`
- `gs_type42_append`
- `gs_type42_get_metrics`
- `gs_type42_wmode_metrics`
- `gs_type42_default_get_metrics`
- `gs_type42_get_outline_from_TT_file`
- `gs_type42_enumerate_glyph`
- `gs_type42_glyph_info`
- `gs_type42_glyph_outline`
- `gs_type42_glyph_info_by_gid`

Dependencies:
- Forward-declares glyph cache and cached font/matrix pair types.
- Uses base font structures from `gxfont.h`.

Research notes:
- The file documents a historical mismatch between `numGlyphs` from `loca` and `trueNumGlyphs` from `maxp`, preserving both for compatibility.
- Type 42 code is a major dependency of font copying and CIDFontType 2 handling.
