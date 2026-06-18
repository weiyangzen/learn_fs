# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiscale.c

Interpolated image rendering support for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_0_interpolate`.
- Enables interpolation only for requested, non-mask, portrait images without mask color, alpha, or low-capability target color depth.
- Uses Mitchell filtering by default through `s_IScale_template`; spatial interpolation support is present but disabled.
- Computes stream scale parameters, concrete output color component count, and source/destination dimensions.
- Allocates a combined source/destination line buffer and a stream image scale state.
- Converts input rows to concrete color values when needed, mirrors rows for negative X scale, and feeds the scaling stream.
- `image_render_interpolate` drains scaled rows, remaps concrete samples to device colors, packs pure colors into scanline buffers, and falls back to per-pixel rectangle fills for non-pure device colors.

Notable dependencies:
- Stream interpolation/scaling templates from `siinterp.h` and `siscale.h`.
- Image state from `gximage.h`.
- Device/color mapping helpers from `gxdevice.h`, `gxcmap.h`, and `gxdcolor.h`.

Research notes:
- If interpolation setup is unsupported or allocation/init fails, the strategy clears `penum->interpolate` and lets another renderer handle the image.
- Conservative filtering rules are compiled out by default.
- This Plan 9 version differs from the sibling 9front file in the negative-X 8-bit mirror path: after copying mirrored data it sets `out = q` rather than rounding `out` up to `align_bitmap_mod`, which may matter for the following output-buffer placement.
