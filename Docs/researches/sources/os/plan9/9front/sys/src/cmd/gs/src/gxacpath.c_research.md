# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxacpath.c

Implements a clipping-path accumulation device that converts filled geometry into a clip-list representation.

Key behavior:
- Defines a `gx_device_cpath_accum` device descriptor whose important operations are open, close, fill-rectangle, and default path/trapezoid/triangle rendering fallbacks.
- `gx_cpath_accum_begin` initializes the stack/device object and opens it.
- `gx_cpath_accum_set_cbox` installs an integer clipping box for rectangle accumulation.
- `gx_cpath_accum_end` closes the device, wraps the accumulated list into a temporary clip path, sets bounding/inner/outer boxes, assigns a new ID, and transfers ownership to the destination clip path.
- `gx_cpath_accum_discard` frees accumulated rectangles after an error.
- `gx_cpath_intersect_path_slow` fills an input path through the accumulation device to intersect it with an existing clip path, temporarily forcing default logical operation.
- `accum_fill_rectangle` clips incoming rectangles, updates the aggregate bounding box, appends or merges simple ordered rectangles, and otherwise splits/merges bands to maintain an ordered non-overlapping clip list.

Dependencies:
- Integrates with Ghostscript device, path fill, clip path, logical operation, and memory systems through `gxdevice.h`, `gxpaint.h`, `gzcpath.h`, and `gzacpath.h`.
- Uses `gs_next_ids` from `gsutil.c` to mark clip-path identity changes.

Research notes:
- The file has DEBUG-only validation for clip-list ordering and linked-list consistency.
- The accumulation logic is explicitly defensive because the fill loop may emit approximately ordered, slightly overlapping rectangles.
- The single-rectangle case is optimized and later promoted to a full list with sentinel head/tail nodes when needed.
