# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.h

## Role

Private definitions and descriptor macros for Ghostscript memory devices.

## Main Contents

- Documents the in-memory bitmap representation: contiguous scan lines padded to bitmap alignment, with a scan-line pointer table for faster lookup.
- Defines scan-line access macros such as `declare_scan_ptr`, `setup_rect`, and `mem_copy_byte_rect`.
- Declares generic memory device procedures: `mem_open`, `mem_close`, `mem_get_initial_matrix`, `mem_get_bits_rectangle`, `mem_draw_thin_line`, and word-oriented variants.
- Defines `mem_full_alpha_device`, `mem_full_device`, and `mem_device` descriptor-construction macros.
- Declares memory device prototypes for mono, mapped, true-color, word-oriented, and planar variants.
- Declares RasterOp procedure variants used by multiple implementation files.
- Declares standard monobit palettes `mem_mono_b_w_palette` and `mem_mono_w_b_palette`.

## Design Notes

The descriptor macros enumerate device procedure tables directly. They centralize memory-device procedure layout and make each concrete memory device define only depth, mapping, copy, fill, RasterOp, and get-bits differences.

## Research Notes

This is core Ghostscript raster infrastructure, not OS filesystem code. It is important because many printer and intermediate devices consume or produce these memory rasters.
