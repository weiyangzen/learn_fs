# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.h

## Role

`gdevpdtv.h` declares the generated glyph-attribute table used by pdfwrite font-resource writing.

## Definitions

- `GS_C_PDF_MAX_GOOD_GLYPH` is `21894`.
- `GS_C_PDF_GOOD_GLYPH_MASK` marks glyphs considered acceptable generally.
- `GS_C_PDF_GOOD_NON_SYMBOL_MASK` marks glyphs acceptable for non-symbol handling.
- `gs_c_pdf_glyph_type[]` is the external packed attribute table defined in `gdevpdtv.c`.

## Dependencies

Included by `gdevpdtw.c`. It has no Ghostscript type dependencies beyond standard C declarations.

## Risks And Invariants

The masks and max glyph value are part of the packed-table contract. Any regeneration of `gdevpdtv.c` must update this header consistently.
