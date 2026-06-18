# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.c

Implements Ghostscript default drawing procedures for trapezoids, parallelograms, triangles, thin lines, linear-color shaded fills, and image begin/data/end compatibility dispatch.

Key structures are `trap_line`, which stores exact fixed-point edge stepping state for trapezoid scan conversion, and `trap_gradient`, which stores integer/fractional color-gradient state. The file repeatedly includes `gxdtfill.h` under different macro configurations to generate fill variants for swapped axes, direct/non-direct fills, contiguous fills, and linear-color fills.

Public entry points include `gx_default_fill_trapezoid`, `gx_fill_trapezoid_cf_fd`, `gx_fill_trapezoid_cf_nd`, `gx_default_fill_linear_color_trapezoid`, `gx_default_fill_linear_color_triangle`, `gx_default_fill_parallelogram`, `gx_default_fill_triangle`, `gx_default_draw_thin_line`, `gx_default_begin_image`, `gx_default_begin_typed_image`, `gx_default_image_data`, and `gx_default_end_image`.

Control flow is mostly dispatch and decomposition: rectangles use rectangle fill fast paths, parallelograms and triangles are split into trapezoids, thin horizontal/vertical lines become rectangles, and general thin lines become one-pixel-wide trapezoids. Linear-color trapezoids and triangles check X-gradient overflow, split triangles when needed, and defer scanline painting to device `fill_linear_color_scanline`.

Important dependencies are Ghostscript fixed-point geometry (`gxfixed.h`), device color and procedure tables (`gxdevice.h`, `gxdcolor.h`), image enumeration, and `gxdtfill.h`.

Risks and invariants: fixed-point arithmetic and gradient division are delicate; overflow checks are explicit but narrow. The temporary replacement of device procedures avoids recursion in image dispatch and must be restored on every path. The generated fill variants depend on macro state being correctly undefined between includes.
