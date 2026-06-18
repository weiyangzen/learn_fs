# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.c

Small graphics-state-aware wrapper layer for path fill and stroke operations. It converts the full `gs_state` into device fill/stroke calls using the current device, clip path, flatness, and color.

Key behavior:
- `caching_an_outline_font` detects outline font cache-device rendering and suppresses normal flatness by using `0.0`, preserving higher quality cached glyph outlines.
- `gx_fill_path` resolves the effective clipping path, fills `gx_fill_params`, and dispatches to the current device `fill_path` procedure.
- `gx_stroke_fill` resolves clipping and dispatches to device `stroke_path` with current device color.
- `gx_stroke_add` and `gx_imager_stroke_add` call `gx_stroke_path_only` to append stroked outlines to another path, using graphics-state or imager flatness.

Notable dependencies:
- Graphics state internals: `gzstate.h`.
- Device and color dispatch: `gxdevice.h`, `gxhttile.h`.
- Path and stroke declarations: `gxpaint.h`, `gxpath.h`.
- Font state: `gxfont.h`.

Research notes:
- This file does not implement rasterization itself; it packages state for lower-level fill/stroke implementations and device procedures.
- The clip path is resolved before dispatch, so failures in clipping state prevent device calls.
