# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxacpath.c

Purpose: Implements a device-backed accumulator for clipping paths by collecting filled rectangles into a `gx_clip_list`.

Key entry points:
- `gx_cpath_accum_begin()` initializes an accumulator device.
- `gx_cpath_accum_set_cbox()` constrains accumulation to a clipping box.
- `gx_cpath_accum_end()` converts the accumulated rectangle list into a `gx_clip_path`.
- `gx_cpath_accum_discard()` frees accumulated list state after errors.
- `gx_cpath_intersect_path_slow()` intersects an existing clipping path with a path by rendering through the accumulator.

Important internals:
- `gs_cpath_accum_device` is a mostly-null device descriptor with `fill_rectangle` implemented.
- `accum_open()` initializes an empty list, bbox, and default infinite clip box.
- `accum_close()` finalizes list extrema and validates under debug.
- `accum_alloc_rect()` manages transition from single-rectangle storage to linked-list storage.
- `accum_fill_rectangle()` clips, merges, splits, and inserts rectangles into sorted non-overlapping bands.

Behavior:
- Maintains bounding box and list ordering by y-band then x.
- Optimizes for first rectangle and simple y-adjacent merging.
- Handles overlap by splitting existing and new bands, merging horizontal spans when possible.
- `gx_cpath_intersect_path_slow()` temporarily resets logical operation to default for fill-only clipping accumulation.

Dependencies:
- Uses Ghostscript device API, clipping path/list structures, fill path machinery, fixed/int conversion, device colors, and unique IDs from `gs_next_ids()`.

Notable risks:
- Rectangle-list manipulation is intricate and mutation-heavy; invariants are checked only in debug builds.
- Uses `goto top` for remaining band processing after splits.
