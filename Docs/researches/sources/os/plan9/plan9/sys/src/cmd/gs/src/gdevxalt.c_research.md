# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxalt.c

Alternative/debug X11 devices that wrap a real `x11` target while exposing different Ghostscript color models.

Key responsibilities:
- Defines `gx_device_X_wrapper`, a forwarding device with a 16-entry color cache and an `alt_map_color` procedure.
- Lazily creates a real `gs_x11_device` target with `gs_copydevice`.
- Generic wrapper procs forward open/close/output/sync/get-bits/get-params/put-params and remap color arguments before forwarding drawing calls.
- `x_wrap_copy_color` can remap source pixels into the target byte layout in blocks when target pixels are byte-aligned.
- `x_alt_map_color` maps wrapper color indices to target X pixels, caching small color values.
- Public devices include `x11cmyk`, `x11cmyk2`, `x11cmyk4`, `x11cmyk8`, `x11mono`, `x11gray2`, `x11gray4`, `x11rg16x`, and `x11rg32x`.

Color behavior:
- CMYK variants encode fake CMYK pixels and convert them back to RGB for the target X device.
- Mono and gray variants map fake gray/black-white pixels to RGB values.
- `x11rg16x` and `x11rg32x` use deliberately permuted RGB bit layouts for debugging byte/component handling.
- Alpha color mapping packs complemented alpha into the high byte for alpha-capable paths.

Filesystem relevance:
- None.
