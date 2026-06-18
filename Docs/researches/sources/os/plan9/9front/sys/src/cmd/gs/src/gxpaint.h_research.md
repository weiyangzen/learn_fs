# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.h

Internal fill/stroke interface tying Ghostscript graphics state paths to imager/device procedures.

Key contents:
- Forward declarations for `gs_imager_state`, `gs_state`, `gx_device`, and `gx_device_color`.
- Graphics-state-aware procedures implemented in `gxpaint.c`: `gx_fill_path`, `gx_stroke_fill`, `gx_stroke_add`, and `gx_imager_stroke_add`.
- `gx_fill_params` carries fill rule, subpixel adjustment, flatness, and the `fill_zero_width` flag for making nearly empty rectangles visible.
- `gx_stroke_params` currently carries flatness.
- Declares `gx_adjust_if_empty`, `gx_stroke_path_expansion`, and `gx_stroke_path_only`.
- Provides compatibility macro `gx_stroke_expansion` and direct `gx_fill_path_only` dispatch macro.

Notable dependencies:
- Requires fixed-point, path, and raster-op related types from surrounding includes.
- The lower-level implementations live mostly in fill/stroke modules outside this group.

Research notes:
- The API distinguishes high-level graphics-state-aware wrappers from imager-level procedures that can be called without a full `gs_state`.
- `gx_imager_stroke_add` still requires a device for absolute-length dots.
