# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdu.c

## Purpose
Provides shared PostScript/PDF writer utilities: vector syntax helpers, color output helpers, binary stream writer management, DCT/CCITT filter setup, unsupported get-bits stubs, and overprint compositor handling.

## Key Behavior
- Defines GC structure descriptors for `gx_device_psdf` and `psdf_binary_writer`.
- Provides standard PDF-style fill/stroke color command sets.
- Emits vector state commands:
  - line width, cap, join, miter limit, dash, flatness,
  - rectangle/path primitives.
- Emits generic path operators used by psdf devices.
- `psdf_adjust_color_index` recovers the all-ones CMYK color case normally colliding with `gx_no_color_index`.
- `psdf_set_color` writes compact gray/RGB/CMYK color commands with rounded byte-derived values.
- `psdf_begin_binary` starts binary data output, adding ASCII85 encoding when binary output is disabled.
- `psdf_encode_binary` inserts additional stream filters.
- `psdf_DCT_filter` wraps JPEG/DCT setup with Rows/Columns/Colors parameters and creates the encoder filter.
- `psdf_CFE_binary` configures CCITT Fax encoding.
- `psdf_end_binary` closes the filter chain.
- `psdf_get_bits` and `psdf_get_bits_rectangle` intentionally reject pixel readback for high-level devices.
- `psdf_create_compositor` absorbs overprint compositors because psdf devices handle overprint directly.

## Dependencies
Uses psdf declarations, Ghostscript stream filters, ASCII85, CCITT Fax, JPEG/DCT, param printing, string streams, and overprint compositor detection.

## Research Notes
This is the shared utility implementation backing the declarations in `gdevpsdf.h`. Concrete devices call into it for syntax emission and binary image data handling.
