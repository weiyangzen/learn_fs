# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont.h

Defines interpreter-side font client data and shared font procedures.

Key points:
- Includes `gsccode.h` and `gsstype.h`.
- Defines `font_data`, the interpreter client data attached to library `gs_font` objects.
- Common refs include:
  - font dictionary
  - `BuildChar`, `BuildGlyph`
  - `Encoding`
  - `CharStrings`
  - `GlyphNames2Unicode`
- Union stores font-type-specific refs:
  - Type 1: `OtherSubrs`, `Subrs`, `GlobalSubrs`
  - Type 42/CIDFontType2: `sfnts`, `CIDMap`, `GlyphDirectory`
  - CIDFontType0: `GlyphDirectory`, `GlyphData`, `DataSource`
- Defines `st_font_data` descriptor macro and helpers `pfont_data`, `pfont_dict`.
- Declares:
  - `font_bbox_param`
  - `font_param`
  - `zfont_mark_glyph_name`
  - `zfont_info`

Dependencies and interactions:
- Used by font-building modules (`zfont.c`, `zbfont.c`, `zchar.c`) and character cache marking.
- The design treats refs as an ordinary structure to avoid allocation fragmentation/sandbars.

Research relevance:
- Core interpreter/library boundary for PostScript font objects and GC-visible font metadata.
