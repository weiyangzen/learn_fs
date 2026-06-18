# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcopy.c

`gxpcopy.c` implements path copying with optional flattening, curve monotonizing, stroke-aware flatness adjustment, and fill-time contour merging.

`gx_path_copy_reducing` iterates source segments and emits corresponding destination segments. With `max_fixed` flatness it copies curves directly or monotonizes them. Otherwise it estimates subdivision count with `gx_curve_log2_samples` and emits flattened line segments through `gx_subdivide_curve`. For stroke flattening, it adjusts flatness based on estimated bbox expansion from line width and CTM. With `pco_accurate`, it inserts tangent-preserving endpoint lines and adjusts them using `adjust_point_to_tangent`.

`gx_path__check_curves` tests whether curves already satisfy requested monotonic/small-curve constraints. `gx_curve_monotonize` finds X/Y derivative roots, orders and merges split parameters, then emits cubic pieces. `gx_curve_monotonic_points` performs fixed-point prefilters before solving derivative roots.

The optimization section searches nearby subpaths for quasi-colinear vertical contacting segments and merges contours by rotating one subpath into another. This is explicitly heuristic, bounded by short search windows, and intended to help the filling algorithm.

Risks include complex fixed/double rounding, manual segment rewiring in contour merging, and comments noting simplified/incomplete behavior.
