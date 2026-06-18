# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.c

`gxpaint.c` implements graphics-state-aware fill/stroke wrappers. It includes state, device, halftone tile, path, paint, and font headers.

The helper `caching_an_outline_font` detects when the graphics state is inside cache-device processing for non-user-defined outline fonts. In that case fill/stroke flattening uses flatness `0.0`, which preserves better outline fidelity for cached glyphs.

`gx_fill_path` obtains the current device, resolves the effective clip path, builds `gx_fill_params`, and dispatches the device `fill_path` procedure. It passes the fill rule, pixel adjustment values, flatness, and whether zero-width/height rectangles should still render.

`gx_stroke_fill` similarly resolves device and clip path, builds `gx_stroke_params`, and calls the device `stroke_path` procedure with the current device color. `gx_stroke_add` and `gx_imager_stroke_add` convert strokes into another path through `gx_stroke_path_only`; the former uses a full `gs_state`, the latter only an imager state plus device.

This file is a thin adapter layer. Its main integration point is the device procedure table. Errors are propagated from clip resolution and device calls.
