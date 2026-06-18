# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.c

## Role

`gdevpdtv.c` is generated glyph metadata for pdfwrite. It contains `gs_c_pdf_glyph_type[]`, a packed table of glyph attributes for glyph IDs up to `GS_C_PDF_MAX_GOOD_GLYPH`.

## Data Layout

- The table is generated from encoding sources through `toolbin/encs2c.ps`.
- Attributes are packed four glyphs per byte, least-significant bits first.
- Consumers test masks declared in `gdevpdtv.h` to decide whether a glyph is safe enough to omit a ToUnicode CMap.

## Dependencies

`gdevpdtw.c` uses this table in `pdf_simple_font_needs_ToUnicode()` when deciding whether simple fonts need explicit Unicode mapping. The table has no functions and no local includes.

## Risks And Invariants

- This file is mechanically generated data; manual edits would be high risk unless regenerated from the source encoding files.
- The packing convention must match the lookup expression in `gdevpdtw.c`.
- The max glyph constant in the header must remain consistent with the table length and generation inputs.
