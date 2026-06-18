# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.h

Declares graphics-state path procedures.

Exports:
- Path constructors: newpath, move/line/curve, arc/arcn/arc_add/arcto, closepath.
- Imager-level arc support: `gs_imager_arc_add`, `make_quadrant_arc`.
- Path transforms/accessors: currentpoint, pathbbox/upathbbox, dashpath, flattenpath, reversepath, strokepath.
- Path enumeration: `gs_path_enum_alloc`, init/copy init, next, cleanup.
- Clipping: clippath, initclip, clip, eoclip.

Integration:
- Includes `gspenum.h`.
- Forward-declares `gs_imager_state`, `gx_path`, and `gs_matrix_fixed`.
- `gs_pathbbox` macro maps to `gs_upathbbox(..., false)`.

Risk notes:
- Function prototype ordering includes an old compiler workaround for bool argument placement in `gs_arc_add`.
