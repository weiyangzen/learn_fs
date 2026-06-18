# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0c.h

## Purpose
Declares helper constructors for Type 0 composite font wrappers around CIDFont and Type 42/TrueType font data.

## Declared Constructors
- `gs_font_type0_from_cidfont`: creates a Type 0 wrapper for a CIDFont, with optional matrix.
- `gs_font_type0_from_type42`: creates a Type 0 wrapper for a Type 42 font converted to Type 2 CIDFont, optionally using the TrueType cmap as the CMap.
- `gs_font_cid2_from_type42`: creates a CIDFontType 2 object from Type 42.
- `gs_cmap_from_type42_cmap`: creates a Unicode-marked CMap from a TrueType cmap, limited to Platform 3, Encoding 1, Format 4.

## Dependencies
Includes `gxfont0.h` and `gxfcid.h`, tying composite-font wrapping to CID font internals and Type 42 support.
