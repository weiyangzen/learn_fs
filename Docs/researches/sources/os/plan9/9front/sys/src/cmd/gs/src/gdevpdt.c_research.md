# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.c

Small initialization module for `pdfwrite` text data. It allocates and ties together the text subsystem's top-level bookkeeping objects.

Key behavior:
- Defines the GC descriptor for `pdf_text_data_t` through `private_st_pdf_text_data()`.
- Implements `pdf_text_data_alloc`.
- Allocates `pdf_text_data_t`, outline-font bookkeeping, bitmap-font bookkeeping, and text-state bookkeeping.
- Cleans up all partially allocated components if any allocation fails.
- Initializes the text data structure to zero and stores `outline_fonts`, `bitmap_fonts`, and `text_state`.

Notable dependencies:
- Uses `gdevpdfx.h` for `gx_device_pdf`/PDF internals.
- Uses `gdevpdtx.h`, `gdevpdtf.h`, `gdevpdti.h`, and `gdevpdts.h` for text/font data types and allocation helpers.

Research notes:
- This file contains no text processing logic; it is only the construction point for the text subsystem's aggregate state.
- Allocation is defensive: all component pointers are freed on failure before returning `NULL`.
- This is PDF output infrastructure, not filesystem functionality.
