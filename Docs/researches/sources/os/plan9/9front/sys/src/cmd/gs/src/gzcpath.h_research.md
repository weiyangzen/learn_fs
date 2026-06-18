# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzcpath.h

Defines internal clipping-path structures.

Key points:
- `gx_clip_rect_list` wraps a reference-counted `gx_clip_list`.
- `gx_cpath_path_list` records full source paths and fill rules for high-level output of path intersections.
- `gx_clip_path` subclasses `gx_path`, adding local rectangle list, rule, inner/outer boxes, shared rectangle list, path validity flag, path-list chain, and change id.
- Includes GC descriptor macros for clip rectangle lists, path lists, clip paths, and clip-path enumerators.
- Defines `gs_cpath_enum_s`, which can enumerate either a path representation or a rectangle-list representation.
- `gx_cpath_is_shared` tests shared rectangle-list ownership through refcount.

Research notes:
- Clip paths maintain both geometric path and rectangle-list forms when needed.
- Lifetime is split between the path representation and the clip list, each with separate sharing concerns.
