# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade6.c

Implements Ghostscript rendering for Coons patch and tensor-product patch shadings. It parses mesh patch streams, converts patch geometry into tensor control grids, recursively subdivides curved/color-varying patches, inserts wedge/padding fills to avoid dropouts, and ultimately paints trapezoids or triangles through device procedures.

Key behavior:
- `shade_next_patch` decodes patch flags and shared-edge continuation forms, reading coordinates, optional tensor interior points, and vertex colors.
- `gs_shading_Cp_fill_rectangle` and `gs_shading_Tpp_fill_rectangle` initialize mesh/patch fill state, iterate patch records, and call `patch_fill`.
- `Cp_transform` evaluates Coons patches; `Tpp_transform` evaluates tensor-product patches with Bernstein polynomials.
- `init_patch_fill_state` derives color domains, flatness, smoothness, linear-color flags, and optional lazy-wedge storage.
- `patch_fill` builds a normalized `tensor_patch`, optionally informs vector devices of shading coverage, computes sample counts from curve flatness/coordinate limits, fills boundary wedges, and recursively fills the patch body.
- Geometry is decomposed through stripes, quadrangles, triangles, wedges, and trapezoids; code handles axis swapping, semi-open raster intervals, self-intersection checks, monotonicity tests, and fixed-point overflow limits.
- Color handling supports direct vertex colors or function-evaluated parameter colors, monotonicity tests, linearity checks, device accelerated `fill_linear_color_triangle` / `fill_linear_color_trapezoid`, and fallback constant-color subdivision.
- `gx_shade_background` fills a background rectangle as one trapezoid expanded by interpatch padding.

Dependencies:
- Mesh and shading infrastructure from `gxshade.h` and `gxshade4.h`.
- Device painting hooks: `fill_trapezoid`, `fill_path`, `fill_linear_color_triangle`, `fill_linear_color_trapezoid`, and `pattern_manage`.
- Color-space remapping and function evaluation through Ghostscript color APIs.
- Fixed-point path/curve helpers from `gzpath.h`, `gxarith.h`, and curve sampling utilities.
- Debug visualization through `vdtrace.h`.

Research notes:
- This is numerically dense rendering code. It relies heavily on fixed-point arithmetic, selected `int64_t` products, and subdivision limits to keep intersection math bounded.
- The file documents known coverage tradeoffs around transposed trapezoids, self-overlap, wedges, and semi-open scan conversion.
- Several branches are guarded by compile-time feature macros such as `LAZY_WEDGES`, `QUADRANGLES`, `INTERPATCH_PADDING`, `USE_LINEAR_COLOR_PROCS`, and debug/test flags.
- Some repeated orientation checks in `is_x_bended` and `is_y_bended` look copy/pasted, but the surrounding logic is conservative and mainly detects possible bending/self-overlap.
