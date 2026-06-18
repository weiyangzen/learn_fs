# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.c

Generic overprint fill-rectangle implementation for Ghostscript devices.

Key behavior:
- Provides scanline pack/unpack helpers for depths below 8 bits and depths that are multiples of 8.
- `gx_overprint_generic_fill_rectangle` handles non-separable color encodings by reading target pixels, decoding source and destination colors, replacing selected process components, re-encoding pixels, and copying modified scanlines back.
- Selects `get_bits_rectangle` options to retrieve native chunky color data without alpha and with standard alignment/raster behavior.
- Provides replicated fill patterns for 2-bit and 4-bit depths and `replicate_color`.
- `gx_overprint_sep_fill_rectangle_1` handles separable encodings efficiently when color depth divides the fill chunk size, using `bits_fill_rectangle_masked`.
- `gx_overprint_sep_fill_rectangle_2` handles other separable byte-depth cases by byte-wise retain-mask/color merging.
- All routines fit the requested rectangle to the target device and allocate temporary scanline buffers.

Notable dependencies:
- Device APIs from `gxdevice.h`, `gsdevice.h`, and `gxgetbit.h`.
- Bit/bitmap helpers from `gsbitops.h`.
- Public declarations from `gxoprect.h`.

Research notes:
- The file describes itself as a “very slow” generic implementation; faster overprint should be implemented directly in target devices when possible.
- The generic non-separable path is necessarily per-pixel because it must decode/modify/re-encode component values.
