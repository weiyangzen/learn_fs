# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.h

Header for the generated pdfwrite glyph-attribute table.

Key behavior:
- Defines `GS_C_PDF_MAX_GOOD_GLYPH` as `21894`.
- Defines `GS_C_PDF_GOOD_GLYPH_MASK` and `GS_C_PDF_GOOD_NON_SYMBOL_MASK`.
- Declares `extern const unsigned char gs_c_pdf_glyph_type[]`.

Research notes:
- Used by font writing code to interpret the generated table in `gdevpdtv.c`.
- The table and constants support ToUnicode omission decisions for simple fonts.
