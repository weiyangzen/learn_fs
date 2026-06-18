# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtx.h

## Role

`gdevpdtx.h` is the shared internal header for pdfwrite text and fonts. It documents the layer split across text processing, font resources, font descriptors, base fonts, and bitmap fonts.

## Key Definitions

- Describes the layer structure: `gdevpdtt.c`, `gdevpdtc.c`, `gdevpdte.c`, `gdevpdts.c`, `gdevpdtf.c`, `gdevpdtw.c`, `gdevpdtd.c`, `gdevpdtb.c`, and bitmap font files.
- Forward-declares opaque `pdf_bitmap_fonts_t`, `pdf_outline_fonts_t`, and `pdf_text_state_t`.
- Defines `pdf_text_data_t`, holding pointers to outline-font, bitmap-font, and text-state subcomponents.
- Provides the GC descriptor macro `private_st_pdf_text_data()`.
- Declares `pdf_font_id()` and `pdf_used_charproc_resources()`.

## Dependencies

Includes `gdevpdt.h` and depends on pdfwrite resource and Ghostscript GC descriptor infrastructure.

## Risks And Invariants

The layering comments are a design contract: higher text layers should not reach around lower font/resource abstractions. The `pdf_text_data_t` GC descriptor must stay synchronized with its pointer fields.
