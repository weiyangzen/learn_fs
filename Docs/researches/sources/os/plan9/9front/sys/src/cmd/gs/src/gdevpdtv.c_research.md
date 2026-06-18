# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.c

Generated glyph-class data for pdfwrite font emission.

Key behavior:
- Defines `const unsigned char gs_c_pdf_glyph_type[]`.
- The array stores glyph attributes for every glyph up to `GS_C_PDF_MAX_GOOD_GLYPH`.
- Attributes are packed four glyphs per byte, least-significant bits first.
- The file was mechanically generated from Ghostscript encoding sources via `toolbin/encs2c.ps`.
- It is consumed by `gdevpdtw.c` in `pdf_simple_font_needs_ToUnicode` to decide whether simple-font glyph mappings are safe enough without writing a ToUnicode CMap.

Research notes:
- This file is almost entirely data, not executable logic.
- The companion header defines the max glyph and bit masks used to interpret this packed table.
