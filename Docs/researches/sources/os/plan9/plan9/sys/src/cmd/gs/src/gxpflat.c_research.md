# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpflat.c

`gxpflat.c` provides Bezier curve flattening utilities for path copying and rasterization.

`gx_curve_log2_samples` estimates the power-of-two subdivision count needed to meet flatness, using a DEC PRL formula based on second differences. It handles very short curves and zero flatness specially for character outlines.

`split_curve_midpoint` bisects a cubic using overflow-conscious midpoint arithmetic. `curve_coeffs_ranged` converts control points to polynomial coefficients and rejects cases too large for the fast fixed-point iterator.

`gx_flattened_iterator__init` initializes a finite-difference iterator for monotonic nonzero curves, computing first/second/third differences with remainder masks. `gx_flattened_iterator__init_line` handles lines and splits very long lines to avoid coordinate-difference overflow in later algorithms. `gx_flattened_iterator__next` and `__prev` step forward/backward through flattened segments, with a compact special path for small `k`. `__switch_to_backscan` adjusts accumulator state before reverse scanning.

`gx_subdivide_curve_rec` emits line segments in bounded batches. If coefficient ranges are too large, it recursively midpoint-splits the curve. `gx_subdivide_curve` is the public wrapper.

This file is numerically sensitive: it mixes fixed-point overflow guards, recursive fallback, debug tracing, and finite-difference state.
