# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.c

Ghostscript default polygon, line, trapezoid, gradient-fill, and image-dispatch device procedures. This is shared rendering infrastructure used when a device does not provide specialized drawing implementations.

Key behavior:
- Defines fixed-point trapezoid edge state (`trap_line`) and gradient state (`trap_gradient`) helpers for exact scan conversion.
- Includes `gxdtfill.h` repeatedly under different macro configurations to generate trapezoid fill variants: axis-swapped/non-swapped, direct/non-direct color writes, contiguous fills, and linear-color fills.
- `gx_default_fill_trapezoid` selects a generated fill routine based on axis orientation and whether the drawing color can be written directly.
- Linear-color routines fill shaded trapezoids and triangles by deriving per-edge and per-scanline color gradients, with overflow checks that return `0` when callers must subdivide.
- `gx_default_fill_parallelogram` and `gx_default_fill_triangle` decompose non-rectangular shapes into trapezoids while preserving Ghostscript’s center-of-pixel rules.
- `gx_default_draw_thin_line` handles horizontal/vertical one-pixel lines as rectangles and general lines as thin trapezoids.
- Image entry points bridge legacy `begin_image` to `begin_typed_image`, avoiding recursive device-procedure calls, and keep obsolete `image_data`/`end_image` compatibility wrappers.

Notable dependencies:
- Ghostscript fixed-point geometry, device, color, image, and clipping APIs: `gxfixed.h`, `gxdevice.h`, `gxdcolor.h`, `gxiparam.h`, `gxistate.h`.
- Macro-generated trapezoid implementation from `gxdtfill.h`.
- Visual debug tracing via `vdtrace.h`.

Research notes:
- This file is core Ghostscript rendering machinery, not filesystem code.
- The implementation is deliberately macro-heavy: actual trapezoid bodies come from `gxdtfill.h` with local macro settings, so behavior depends on compile-time inclusion context.
- Linear shading has explicit overflow avoidance and returns non-error `0` to request decomposition by higher-level callers.
- The obsolete `gx_default_draw_line` intentionally returns `-1`; newer thin-line and shape fill procedures are the meaningful paths.
