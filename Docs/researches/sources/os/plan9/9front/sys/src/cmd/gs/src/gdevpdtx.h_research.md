# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtx.h

Shared pdfwrite text/font implementation definitions.

Key behavior:
- Includes `gdevpdt.h`.
- Documents the layering of pdfwrite text code: text processing, font resources, font descriptors, base fonts, and bitmap font processing.
- Forward-declares opaque text/font state components: `pdf_bitmap_fonts_t`, `pdf_outline_fonts_t`, and `pdf_text_state_t`.
- Defines `pdf_text_data_s`, grouping outline font data, bitmap font data, and text-state data.
- Provides the GC descriptor macro for `pdf_text_data_t`.
- Forward-declares `pdf_font_resource_t`.
- Declares `pdf_font_id` and `pdf_used_charproc_resources`.

Research notes:
- This is a small architectural header; its layer comment is the main map for the `gdevpdt*` text/font subsystem.
