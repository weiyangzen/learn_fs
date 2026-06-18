# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiscale.c

Interpolated image rendering support for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_0_interpolate`.
- Enables interpolation only for a limited set of cases: interpolated, non-mask, portrait images without mask color, alpha, or low-capability target color depth.
- Uses Mitchell filtering by default via `s_IScale_template`; spatial interpolation code path is present but disabled.
- Allocates a source/destination line buffer and a stream image scale state.
- Converts input rows to concrete color values when needed, optionally mirrors rows for negative X scale, and feeds the scaling stream.
- `image_render_interpolate` drains scaled rows, remaps concrete output samples to device colors, packs pure colors into scanlines, and falls back to per-pixel rectangle fills for non-pure device colors.

Notable dependencies:
- Stream scaling/interpolation templates from `siinterp.h` and `siscale.h`.
- Image state from `gximage.h`.
- Device/color mapping helpers from `gxdevice.h`, `gxcmap.h`, and `gxdcolor.h`.

Research notes:
- If interpolation setup is unsupported or allocation/init fails, the strategy clears `penum->interpolate` and lets another renderer handle the image.
- Conservative filtering rules are compiled out by default.
