# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcopy.c

Path copying, curve flattening orchestration, curve monotonization, and contour-merge optimization code.

Key behavior:
- `gx_path_copy_reducing` copies a path while optionally preserving curves, flattening curves, monotonizing curves, applying accurate tangent endpoints, or adjusting flatness for stroking.
- Stroke-aware flattening reduces flatness according to a conservative expansion estimate based on CTM and line half-width.
- Accurate flattening inserts extra tangent line segments and adjusts endpoints to align better with curve tangents.
- `adjust_point_to_tangent` handles vertical, horizontal, and general tangent projection cases.
- `gx_path__check_curves` tests whether curves already satisfy monotonic/small-curve constraints.
- `gx_curve_monotonize` splits a Bezier at derivative roots in X and Y so resulting curve spans are monotonic.
- `gx_curve_monotonic_points` computes valid derivative-zero parameters with several cheap rejection cases before using square roots.
- `gx_path_merge_contacting_contours` searches nearby subpaths for quasi-vertical contacting line segments and splices contours together for fill optimization.

Notable dependencies:
- `gconfigv.h` for FPU configuration.
- `gxistate.h` for line parameters.
- `gzpath.h` for segment internals.
- Fixed arithmetic helpers from `gxfixed.h`/`gxfarith.h`.

Research notes:
- On copy error, the destination path is reset with `gx_path_new`, avoiding partially reduced output.
- The contour merge is explicitly simplified and heuristic: it searches limited windows and only quasi-vertical contacts.
- In `gx_curve_monotonize`, the statements assigning `ry = -qy` in two sign-noise branches look suspicious because they mirror `rx = -rx` but use `qy` rather than `ry`.
