# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.c

## Purpose
Small initialization module for `pdfwrite` text state. It allocates the aggregate `pdf_text_data_t` object used by `gx_device_pdf`.

## Main Logic
- Registers the GC descriptor for `pdf_text_data_t` using `private_st_pdf_text_data()`.
- Implements `pdf_text_data_alloc(gs_memory_t *mem)`.
- Allocates three subordinate components:
  - `pdf_outline_fonts_t` via `pdf_outline_fonts_alloc`.
  - `pdf_bitmap_fonts_t` via `pdf_bitmap_fonts_alloc`.
  - `pdf_text_state_t` via `pdf_text_state_alloc`.
- Frees all partially allocated components if any allocation fails.
- Zeroes the aggregate and installs the three component pointers.

## Integration
- Called by the PDF device initialization path declared through `gdevpdfx.h`/`gdevpdt.h`.
- Bridges the layered text/font subsystem into one object stored at `pdev->text`.
- Depends on `gdevpdtx.h`, `gdevpdtf.h`, `gdevpdti.h`, and `gdevpdts.h`.

## Risks and Notes
- Allocation is all-or-nothing and returns `0` on failure rather than a Ghostscript error code.
- The aggregate only stores pointers; ownership/lifetime of component internals is managed by the Ghostscript allocator/GC descriptors.
