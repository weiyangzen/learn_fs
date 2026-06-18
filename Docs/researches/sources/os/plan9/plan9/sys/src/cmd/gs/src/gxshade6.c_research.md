# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade6.c

Ghostscript renderer for Coons patch and tensor-product patch shadings. It turns shading mesh patch streams into device trapezoids, triangles, wedges, and optionally device-native linear-color fills while preserving contiguous scan conversion as much as possible.

Key behavior:
- `gs_shading_Cp_fill_rectangle` and `gs_shading_Tpp_fill_rectangle` initialize mesh fill state, parse patch records with `shade_next_patch`, and call `patch_fill`.
- `shade_next_patch` handles patch flags 0-3, reuses prior patch edges where allowed by the PDF/PostScript mesh format, reads Bezier boundary control points, optional tensor interior points, and vertex colors.
- `Cp_transform` evaluates Coons patch coordinates from the four boundary curves; `Tpp_transform` evaluates tensor-product patches using Bernstein basis functions and a 4x4 control grid.
- `make_tensor_patch` normalizes both Coons and tensor patches into an internal `tensor_patch` with four corner colors; Coons interiors are synthesized from boundary control points.
- `patch_fill` computes subdivision counts from curve flatness, informs devices that support `pattern_manage__shading_area`, fills interpatch padding/wedges, and recursively decomposes patches.
- The decomposition path uses `fill_patch`, `fill_stripe`, `decompose_stripe`, `fill_quadrangle`, `mesh_triangle`, and triangle helpers to split geometry until it can be painted as constant-color trapezoids or linear-color primitives.
- Wedge logic tracks thin gaps introduced by different curve subdivision levels. With `LAZY_WEDGES`, wedge vertices are pooled and linked so gaps can be filled later without overfilling every subdivision immediately.
- Color handling supports direct interpolated component colors and function-based colors. It tests monotonicity, linearity, and smoothness with `gs_function_is_monotonic`, `cs_is_linear`, `function_linearity`, and `color_span`.
- When possible, it uses device procedures `fill_linear_color_triangle` and `fill_linear_color_trapezoid`; otherwise it recursively decomposes to constant-color trapezoids via `fill_trapezoid`.
- `gx_shade_background` paints a padded rectangular shading background using a trapezoid.

Notable dependencies:
- Mesh/shading infrastructure: `gxshade.h`, `gxshade4.h`.
- Color-space and device color remapping: `gxcspace.h`, `gxdcolor.h`.
- Device procedures: `gxdevcli.h`, especially `fill_trapezoid`, `fill_path`, `pattern_manage`, and linear-color fills.
- Path/fixed-point helpers: `gzpath.h`, `gxarith.h`, `stdint_.h`.

Research notes:
- The file is graphics/rendering code in the Plan 9 vendored Ghostscript tree, not filesystem logic.
- It is heavily fixed-point and `int64_t` oriented. Comments document deliberate limits for `intersection_of_small_bars` and curve subdivision to avoid overflow in self-intersection handling.
- Coverage correctness is central: comments describe semi-open device scan conversion, transposed trapezoids, interpatch padding, dropout prevention, and known double-paint tradeoffs.
- Recursion has safety guards such as `level > 100`, but many paths rely on subdivision heuristics and assertions around lazy wedge buffer sizing.
- There are repeated orientation checks in `is_x_bended` and `is_y_bended`, suggesting copy/paste duplication in a conservative self-overlap detector.
