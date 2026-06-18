# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfarith.h

This header supplies floating-point arithmetic helpers and optimized comparison macros for platforms with slow or absent FPUs. It includes `gconfigv.h` for `USE_FPU` and `gxarith.h`.

When `USE_FPU <= 0`, floats are IEEE, and float size matches integer or long size, the header redefines selected `gxarith.h` macros to inspect float/double bit patterns. Optimized macros include `is_fzero`, `is_fzero2`, `is_fneg`, `is_fge1`, `f_fits_in_ubits`, and `f_fits_in_bits`. They handle sign bits, zero representations, exponent masks, and integer-bit-fit tests without conventional floating comparisons where possible.

The header also declares degree-based trigonometric helpers: `gs_sin_degrees`, `gs_cos_degrees`, `gs_sincos_degrees`, and `gs_atan2_degrees`. `gs_sincos_t` records sine, cosine, and whether the angle is orthogonal. The degree functions are intended to hit exact values at multiples of 90 degrees and follow PostScript quadrant behavior for atan2.

Filesystem relevance: none. It is math support for rendering geometry.
