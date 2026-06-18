# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont42.h

Declares Type 42 and CIDFontType 2 TrueType font build helpers.

Key points:
- `build_gs_TrueType_font` builds Type 11 or Type 42 fonts.
- `font_string_array_param` validates/extracts string arrays while returning the value even on wrong type.
- `font_GlyphDirectory_param` returns 0 if present, 1 if absent, or an error.
- `font_gdir_get_outline` retrieves glyph outlines from `GlyphDirectory`, returning an empty string if missing or out of range.
- `string_array_access_proc` accesses byte ranges across arrays of strings, used for `sfnts` and `CIDMap`.

Research relevance:
- Interface for interpreter-side TrueType and CID TrueType font materialization.
