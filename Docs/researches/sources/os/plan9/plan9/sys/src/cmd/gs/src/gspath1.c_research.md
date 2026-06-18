# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath1.c

Implements additional PostScript Level 1 path operations: arcs, arcto, path transformations, bounding boxes, and path enumeration.

Key functions:
- Arc support: `gs_arc`, `gs_arcn`, `gs_arc_add`, `gs_imager_arc_add`, `next_arc_curve`, `next_arc_quadrant`, `arc_add`.
- `gs_arcto`: computes tangent points and arc curve between two segments.
- `make_quadrant_arc`: computes Bezier control points for quadrant arcs.
- `gs_dashpath`: expands dash pattern into path.
- `gs_flattenpath`: converts curves to line segments.
- `gs_reversepath`: reverses subpath order and updates current/subpath start points.
- `gs_upathbbox`: returns path bbox in user coordinates.
- `gs_path_enum_copy_init`, `gs_path_enum_next`, `gs_path_enum_cleanup`.

Integration:
- Uses low-level `gx_path` operations and matrix transforms.
- Arc code transforms from user to fixed device coordinates and tags arc-generated curve segments.
- Path enumeration transforms fixed device points back into user space.

Risk notes:
- Arc approximation is numerically sensitive, with special fast paths for orthogonal quadrant arcs.
- `gs_arcto` handles collinearity by falling back to `lineto`.
- Enumeration may allocate a path copy, so cleanup is mandatory when `copy` is true.
