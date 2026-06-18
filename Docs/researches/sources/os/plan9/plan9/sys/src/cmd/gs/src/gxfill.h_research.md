# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.h

## Purpose
Defines common internal data structures, macros, and statistics for the path filling algorithm and dropout-prevention integration.

## Main Types
- `active_line`: state for a segment/flattened curve active in the scan conversion process.
- `fill_options`: immutable options passed through fill loops, including device/color state, fill rule, adjustment, clipping box, direct-fill capability, and backend flags.
- `line_list`: per-fill transient state containing active-line pools, Y/X lists, horizontal lists, margin sets, local storage, and bbox dimensions.

## Important Macros
- `AL_X_AT_Y`: computes an active line's X coordinate at a fixed Y, with a fast integer path and a slower quotient path.
- `SET_NUM_ADJUST` / `ADD_NUM_ADJUST`: compensate for architecture-specific negative division behavior.
- `LOOP_FILL_RECTANGLE_DIRECT`: selects direct device rectangle fill versus ROP-aware rectangle fill based on template-time `FILL_DIRECT`.

## Local Storage Strategy
Provides stack/local arrays for common small fills:
- `MAX_LOCAL_ACTIVE`
- `MAX_LOCAL_SECTION`
- `local_active`
- `local_margins`
- `local_section0`
- `local_section1`

Dynamic allocation is reserved for unusually complex fills.

## Debug Support
When `DEBUG` is enabled, defines `stats_fill_t` counters and `INCR` macros used throughout `gxfill.c` and template headers.
