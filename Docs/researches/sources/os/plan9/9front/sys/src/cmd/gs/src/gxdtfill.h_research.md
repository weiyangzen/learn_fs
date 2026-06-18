# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdtfill.h

This header is a configurable trapezoid-fill algorithm intended to be included multiple times with different macro settings. It is not a conventional declaration header; it expands into a concrete `GX_FILL_TRAPEZOID` function based on configuration macros such as `CONTIGUOUS_FILL`, `SWAP_AXES`, `FILL_DIRECT`, `LINEAR_COLOR`, `EDGE_TYPE`, and `FILL_ATTRS`.

The long comment specifies PostScript scan conversion rules for pixels whose centers fall inside trapezoid edges, the behavior difference when contiguous fill is enabled, and the rational-floor math used to avoid off-by-one errors around half-pixel boundaries and fixed-point epsilon.

The generated function computes sampled Y bounds, initializes left and right `trap_line` edge walkers, handles vertical-edge rectangle fast paths for non-linear colors, computes `dx/dy` using overflow-aware quotient helpers, and iterates scanline spans. For ordinary fills it batches consecutive scanlines with identical left/right integer bounds into taller rectangles. For linear-color fills it computes per-scanline gradients and delegates to the device `fill_linear_color_scanline` proc.

The contiguous-fill mode can widen dropout-prone narrow spans and connect adjacent rectangles to keep filled regions contiguous, while avoiding extra peak pixels when flags indicate peaks.

The implementation uses device color fill indirection or direct device `fill_rectangle` depending on `FILL_DIRECT`, supports swapped axes, emits visual debugging rectangles under debugging macros, checks interrupts before returning, and undefines its configuration/helper macros at the end.

Filesystem relevance: none. It is scan conversion/rasterization logic.
