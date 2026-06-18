# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpflat.c

Bezier curve flattening algorithms and iterator support for converting curves into line segments.

Key behavior:
- `gx_curve_log2_samples` estimates `log2` sample count from DEC PRL flatness bounds, with special handling for short curves and flatness zero.
- `split_curve_midpoint` bisects a cubic Bezier using overflow-aware fixed-point midpoints.
- `curve_coeffs_ranged` checks whether polynomial coefficients and sample count fit the fast fixed-point iterator range.
- `gx_flattened_iterator__init` precomputes finite differences for a monotonic curve and stores current/end state.
- `gx_flattened_iterator__init_line` represents long lines as two segments when endpoint subtraction may overflow.
- `gx_flattened_iterator__next` and `gx_flattened_iterator__prev` scan flattened segments forward/backward using accumulated fixed-point deltas and remainders.
- `gx_flattened_iterator__switch_to_backscan` adjusts iterator state when changing scan direction.
- `gx_subdivide_curve_rec` falls back to recursive midpoint subdivision when the fast iterator cannot represent a curve safely, batching generated points into line additions.
- `gx_subdivide_curve` is the public wrapper around recursive subdivision.

Notable dependencies:
- `gxarith.h`, `gxfixed.h`, and concrete path internals in `gzpath.h`.
- `vdtrace.h` for optional visual debugging.

Research notes:
- The file favors fast fixed-point iteration but recursively subdivides to avoid coefficient overflow.
- `max_points` limits batched line generation, reducing stack/local buffer size while still streaming long flattened output.
- Comments include several old spelling mistakes, but the algorithmic intent is well documented.
