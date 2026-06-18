# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zbfont.c

This is a central Ghostscript font construction utility file for base, simple, primitive, outline, Type 3, and FDArray-backed fonts.

Key behavior:
- Implements `.buildfont3` for Type 3 user-defined fonts.
- Provides glyph encoding helpers: character-to-glyph lookup through `Encoding`, glyph-name lookup, CID numeric-name fabrication, and glyph-to-Unicode mapping via `GlyphNames2Unicode` or a `UnicodeDecoding` resource.
- Builds common font procedure references from `BuildChar` and `BuildGlyph`.
- Implements common builders:
  - `build_gs_font`
  - `build_gs_sub_font`
  - `build_gs_simple_font`
  - `build_gs_outline_font`
  - `build_gs_primitive_font`
  - `build_gs_FDArray_font`
- Validates font dictionaries for `FontType`, `Encoding`, `FontMatrix`, `FontBBox`, `PaintType`, `StrokeWidth`, bitmap policy keys, UID, and FID behavior.
- Handles re-registered/scaled fonts, re-encoded fonts, and Type 0/CID FDArray subfont construction.
- Initializes `font_data`, stores font dictionary/procs/encoding, assigns glyph and Unicode procedures, and registers fonts through `define_gs_font`.

Important dependencies:
- Uses Ghostscript font core headers: `gxfont.h`, `bfont.h`, `gscencs.h`, `gsmatrix.h`.
- Uses interpreter dictionary/name/ref memory APIs: `idict.h`, `idparam.h`, `iname.h`, `ialloc.h`, `istruct.h`.

Research notes:
- This file is high-value for understanding Ghostscript’s PostScript dictionary-to-C font object bridge.
- It contains compatibility accommodations for malformed or non-standard fonts, including synthetic glyph names for Type 3 `.notdef` cases and UID invalidation when metrics differ.
