# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.c

Implementation of Ghostscript clipping paths and clipping rectangle lists.

Key behavior:
- Defines structure descriptors and GC relocation/enumeration logic for clip paths, clip lists, clip rects, clip path-list nodes, clip enumerators, and clipping devices.
- Manages clipping path allocation, local/shared initialization, reference counting, assignment, unsharing, and freeing.
- Maintains both path-segment and rectangle-list representations, with validity flags and cached inner/outer boxes.
- Converts rectangle-list-only clipping paths back into path segments via `gx_cpath_to_path`.
- Implements fast rectangle clipping/intersection paths and falls back to slow path intersection for nontrivial clipping.
- Tracks previous clipping paths in `gx_cpath_path_list` when nontrivial intersections need clippath reconstruction history.
- Scales clipping paths and rectangle lists by powers of two.
- Initializes/free clip lists and converts fixed rectangles into integer clip rectangles.
- Enumerates rectangle-list clipping paths as path edges through `gx_cpath_enum_init` and `gx_cpath_enum_next`.
- Provides debug printing for clip paths and rectangle lists.

Notable dependencies:
- Path, clipping accumulator, fixed-point geometry, graphics state, and memory/reference-counting infrastructure.

Research notes:
- Rectangle clipping is optimized heavily; a clip path may be represented only as a rectangle list until a path representation is demanded.
- `gx_cpath_unshare` has an explicit NYI for copying shared rectangle lists; callers should be cautious around shared-list mutation.
- The rectangle-list enumerator traces left/right edges and may produce many small line segments for complex clip lists.
