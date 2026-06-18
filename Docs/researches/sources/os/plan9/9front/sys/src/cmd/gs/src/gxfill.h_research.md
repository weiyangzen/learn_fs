# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.h

Defines shared structures and macros for the fill algorithm and dropout prevention.

Key definitions:
- `active_line` stores segment endpoints, deltas, current/next X, direction, curve iterator, monotonicity flags, and list links.
- `AL_X_AT_Y` computes edge X at a given Y with a fast fixed-point path and slower quotient fallback.
- `fill_options` packages device color, RasterOp, clipping box, fill rule, adjustment values, flatness, device callbacks, and algorithm flags.
- `line_list` owns pending Y list, active X list, horizontal-line lists, margin sets, local allocation pools, bbox fields, and fill options.
- `LOOP_FILL_RECTANGLE_DIRECT` switches between pure-color device fill and RasterOp-aware rectangle fill.
- Debug-only `stats_fill_t` tracks counters for allocation, sorting, banding, crossings, and fill operations.

Dependencies:
- Requires `active_line` users to know `segment`, `gx_flattened_iterator`, `gx_device`, `gx_device_color`, and `margin_set`.
- Consumed by `gxfill.c`, `gxfdrop.c`, and the fill template headers.

Research notes:
- This header exposes internal fill-engine state, not a stable public graphics API.
- The local arrays avoid allocator churn for common small fills; large/complex fills fall back to dynamic allocation.
