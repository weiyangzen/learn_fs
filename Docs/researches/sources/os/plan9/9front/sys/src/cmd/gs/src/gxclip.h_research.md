# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.h

Internal shared definitions for Ghostscript clipping callback dispatch.

Key behavior:
- Defines `clip_callback_data_t`, a single closure structure used by both rectangle-list clipping and mask clipping.
- Stores the target device, original rectangle geometry, source bitmap fields, colors, mask/fill parameters, tile phase, RasterOp texture/source color arrays, and drawing color.
- Declares callback helpers for fill rectangle, copy mono, copy color, copy alpha, fill mask, strip tile rectangle, and strip copy RasterOp.

Dependencies:
- Requires surrounding Ghostscript types such as `gx_device`, `gx_color_index`, `gx_drawing_color`, `gx_clip_path`, `gx_strip_bitmap`, `gs_int_point`, and `gs_logical_operation_t`.

Research notes:
- The struct deliberately over-approximates callback data for multiple operations to reduce duplicate small closure types.
- The callback ABI uses clipped rectangles as `[xc, xec) x [yc, yec)` target coordinates.
