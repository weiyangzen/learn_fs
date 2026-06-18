# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid1.c

## Purpose
Implements Ghostscript interpreter operators for CIDFontType 1 and CIDFontType 2 fonts: `.buildfont10`, `.buildfont11`, CID-to-TrueType glyph mapping, and CIDMap construction support.

## Key Functions
- `zbuildfont10()` builds FontType 10 user-defined CID fonts, collecting build procedures and `CIDSystemInfo`.
- `z11_CIDMap_proc()` maps CID glyphs to TrueType glyph numbers from a string, integer offset, dictionary, or string-array CIDMap.
- `zbuildfont11()` builds CIDFontType 2 / FontType 11 TrueType CID fonts, including optional disk-file glyph caching and CIDMap validation.
- `ztype11mapcid()` exposes CID-to-GID mapping to PostScript.
- `zfillCIDMap()` delegates CIDMap population to `cid_fill_CIDMap()`.

## Important Behavior
- FontType 11 accepts CIDMap data as string/string-array, dictionary, or integer offset; string-based maps require nonzero `GDBytes`.
- `MetricsCount` must be 0, 2, or 4 and causes glyph data accessors to skip leading metric words.
- If the font dictionary has `File` and table offsets for `loca`/`glyf`, the font can cache glyph data from the TrueType file.

## Research Notes
This file bridges PostScript CID font dictionaries to Ghostscript's Type 42 TrueType engine.
