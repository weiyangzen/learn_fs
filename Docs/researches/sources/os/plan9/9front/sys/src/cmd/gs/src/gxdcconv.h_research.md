# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.h

This small internal header declares Ghostscript device color conversion entry points over fractional color components. It includes `gxfrac.h` for the `frac` representation and exposes RGB/CMYK/gray conversion helpers that take a `const gs_imager_state *` so transfer/color rendering state can influence conversions.

The API surface is four declarations: `color_rgb_to_gray`, `color_rgb_to_cmyk`, `color_cmyk_to_gray`, and `color_cmyk_to_rgb`. The RGB/CMYK conversion routines write into caller-provided arrays (`frac cmyk[4]` and `frac rgb[3]`), while gray conversion returns a single `frac`.

Filesystem relevance: none directly. This belongs to the bundled Ghostscript rendering stack under 9front and is graphics/color infrastructure, not Plan 9 VFS or storage code.
