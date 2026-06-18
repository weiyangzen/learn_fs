# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.h

Private definitions and device-construction macros for Ghostscript memory devices.

- Documents the contiguous bitmap representation: scan lines in PostScript-like order, padded to `bitmap_align_mod`, plus a line-pointer table for faster row access.
- Defines scan-line setup/access macros such as `declare_scan_ptr`, `setup_rect`, and `SETUP_RECT_VARS`.
- Declares generic memory-device procs: open, close, initial matrix, get-bits rectangle, word get-bits rectangle, mapped color encode/decode, default RasterOp, and `mem_draw_thin_line`.
- Provides `mem_full_alpha_device`, `mem_full_device`, and `mem_device` macros for generating full `gx_device_memory` descriptors and procedure tables.
- Defines max-value macros for supported RGB/gray depths, working around compiler shift-expression issues.
- Declares byte-rectangle utilities: `mem_swap_byte_rect` and `mem_copy_byte_rect`.
- Exposes memory-device prototypes for mono, mapped 2/4/8-bit, true-color 16 through 64-bit, planar, and word-oriented variants.
- Declares shared RasterOp entry points for mono, gray, and gray8/rgb24 memory devices.
- Exposes the two standard 1-bit palettes used by `gdevmem.c`.
