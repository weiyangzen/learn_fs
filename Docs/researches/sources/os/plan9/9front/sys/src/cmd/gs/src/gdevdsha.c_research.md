# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsha.c

Ghostscript default shading scanline fill implementation.

Key behavior:
- Implements `gx_default_fill_linear_color_scanline`.
- Decomposes a horizontally varying linear-color scanline into runs of constant device color index.
- Builds initial packed color index from component fractions and device component shifts/bits.
- Steps each component by numerator/denominator gradient arithmetic, preserving fractional remainders.
- Clips each run against the fill clip rectangle.
- Emits each run through `fill_rectangle`, swapping axes when requested by the fill attributes.
- Emits visual debug rectangles via `vd_rect`.

Notable dependencies:
- Ghostscript device/color index APIs: `gxdevice.h`, `gxcindex.h`.
- Visual debug tracing via `vdtrace.h`.

Research notes:
- This is the fallback scanline shading path; devices can override it with a direct raster implementation.
- The file comments note this default is simple but not optimal because it enumerates color changes and emits rectangles rather than writing scanline pixels directly.
- The clip tests intentionally mirror broader fill clipping behavior.
