# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype42.c

Purpose: Implements Type 42 / TrueType font support: SFNT table parsing, glyph lookup, metrics, outline extraction, and conversion to Ghostscript paths.

Key entry points:
- `gs_type42_font_init()` parses TrueType tables and initializes font procedures.
- `gs_type42_glyph_outline()` appends a glyph outline and advances the current point.
- `gs_type42_glyph_info()` and `gs_type42_glyph_info_by_gid()` return widths, vertical vectors, pieces, and default glyph info.
- `gs_type42_append()` appends a glyph outline for imaging.
- `gs_type42_get_outline_from_TT_file()` reads glyph data directly from a TrueType stream.

Important internals:
- `get_glyph_offset()` reads `loca` entries in short or long format.
- `default_get_outline()` uses `loca`/`glyf` and can make a contiguous copy if the font string provider returns segmented data.
- `parse_component()` decodes composite glyph flags, component transforms, and point matching arguments.
- `total_points()`, `parse_pieces()`, `append_simple()`, `append_component()`, and `check_component()` implement simple/composite glyph handling.
- `append_outline_fitted()` delegates actual fitted TrueType outline production to `gx_ttf_outline()` through cached font/matrix state.

Behavior:
- Accepts TrueType version `0x00010000` and `"true"`.
- Caches glyph lengths in `pfont->data.len_glyphs`, with fallback logic for out-of-order `loca` tables.
- Computes a fallback `FontBBox` from the `head` table when the PostScript `FontBBox` looks invalid.
- Converts quadratic TrueType curves to cubic Beziers for Ghostscript paths.
- Handles composite glyph point matching by doing extra passes to collect component points.

Dependencies:
- Uses `gxttf.h`, `gxttfb.h`, `gxfcache.h`, font notification release hooks, stream helpers, matrix/fixed path APIs, and `gsutil.h` big-endian parsing.

Notable risks:
- Calls `abort()` if `unitsPerEm` is zero in `gs_type42_font_init()`/`recipunitsperem()`.
- Some older outline code remains in-file, but final fitted outline path goes through `gx_ttf_outline()`.
- Composite glyph recursion depends on valid glyph data and can be expensive for deeply nested components.
