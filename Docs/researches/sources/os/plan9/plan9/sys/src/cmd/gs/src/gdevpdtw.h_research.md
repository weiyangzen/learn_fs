# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.h

## Role

`gdevpdtw.h` declares the font and CMap resource writing API for pdfwrite. Its comments state these procedures are intended only for use from `gdevpdtf.c`.

## Exported API

- Font content writers matching `pdf_font_write_contents_proc_t`: Type 0, Type 3 finalization, standard/simple fonts, CIDFontType0, and CIDFontType2.
- Encoding helpers: `pdf_different_encoding_index()`, `pdf_write_encoding()`, and `pdf_write_encoding_ref()`.
- CID/CMap helpers: `pdf_write_cid_system_info()` and `pdf_write_cmap()`.

## Dependencies

The header forward-declares `gs_cid_system_info_t` and `gs_cmap_t`; it requires pdfwrite font/resource types from surrounding includes.

## Risks And Invariants

Callers must pass fully initialized `pdf_font_resource_t` structures whose subtype-specific fields match the writer selected during allocation. The API is intentionally narrow and internal.
