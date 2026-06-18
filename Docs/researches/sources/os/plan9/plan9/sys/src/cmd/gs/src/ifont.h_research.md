# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont.h

Defines interpreter-side font client data and shared font procedures.

Key points:
- Includes `gsccode.h` and `gsstype.h`.
- Defines `font_data`, interpreter client data attached to library `gs_font` objects.
- Common refs include font dictionary, `BuildChar`, `BuildGlyph`, `Encoding`, `CharStrings`, and `GlyphNames2Unicode`.
- Type-specific union stores Type 1, Type 42/CIDFontType2, and CIDFontType0 refs.
- Exports `st_font_data`, `pfont_data`, and `pfont_dict`.
- Declares `font_bbox_param`, `font_param`, `zfont_mark_glyph_name`, and `zfont_info`.

Research relevance:
- Core interpreter/library boundary for PostScript font objects and GC-visible font metadata.
