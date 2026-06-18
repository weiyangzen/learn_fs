# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid1.c

## Purpose
Implements Ghostscript interpreter operators for CIDFontType 1 and CIDFontType 2 fonts: `.buildfont10`, `.buildfont11`, CID-to-TrueType glyph mapping, and CIDMap construction support.

## Key Functions
- `zbuildfont10()` builds FontType 10 user-defined CID fonts, collecting build procedures and `CIDSystemInfo`.
- `z11_CIDMap_proc()` maps CID glyphs to TrueType glyph numbers from a string, integer offset, dictionary, or string-array CIDMap.
- `z11_get_outline()` and `z11_get_metrics()` wrap Type 42 outline/metrics procedures when `MetricsCount` embeds metrics before outline data.
- `z11_glyph_info()`, `z11_enumerate_glyph()`, `z11_get_glyph_index()`, and `z11_glyph_outline()` adapt Type 42 glyph access to CID-keyed fonts.
- `zbuildfont11()` builds CIDFontType 2 / FontType 11 TrueType CID fonts, including optional disk-file glyph caching and CIDMap validation.
- `ztype11mapcid()` exposes CID-to-GID mapping to PostScript.
- `zfillCIDMap()` delegates CIDMap population to `cid_fill_CIDMap()`.

## Important Behavior
- FontType 11 accepts CIDMap data as string/string-array, dictionary, or integer offset; string-based maps require nonzero `GDBytes`.
- `MetricsCount` must be 0, 2, or 4 and causes glyph data accessors to skip leading metric words.
- If the font dictionary has `File` and table offsets for `loca`/`glyf`, the font can cache glyph data from the TrueType file.
- `ztype11mapcid` rejects non-CID TrueType fonts except under `TEST`.

## Research Notes
This file bridges PostScript CID font dictionaries to Ghostscript's Type 42 TrueType engine. It depends heavily on helpers from `zfont42.c`, `ifcid.h`, and Type 1 glyph-info utilities.
