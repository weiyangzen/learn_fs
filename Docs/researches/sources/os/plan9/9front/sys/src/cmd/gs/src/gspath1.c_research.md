# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath1.c

Implements additional PostScript Level 1 path routines: arcs, arc tangents, path transformations, bounding boxes, and path enumeration.

Main behavior:
- `gs_arc`, `gs_arcn`, `gs_arc_add`, and `gs_imager_arc_add` approximate circular arcs with cubic Bezier curves.
- Optimizes exact quadrant arcs when CTM is scale/rotation-friendly.
- `gs_arcto` computes tangent points and adds an arc between two line segments.
- `make_quadrant_arc` computes four control points for quadrant arcs.
- `gs_dashpath`, `gs_flattenpath`, and `gs_reversepath` transform the current path.
- `gs_upathbbox` computes a user-space bounding box from the fixed device-space path.
- `gs_path_enum_copy_init`, `gs_path_enum_next`, and `gs_path_enum_cleanup` enumerate path elements back in user coordinates.

Important dependencies:
- Uses fixed-point geometry, CTM inverse transforms, path segment notes, dash expansion, curve flattening, and local path allocation.
