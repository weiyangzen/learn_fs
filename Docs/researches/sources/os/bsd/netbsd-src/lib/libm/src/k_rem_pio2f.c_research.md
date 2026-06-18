# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_rem_pio2f.c

This file implements the float-specific large-argument reducer `__kernel_rem_pio2f(float *x, float *y, int e0, int nx, int prec, const int32_t *ipio2)`.

Unlike the double kernel, input chunks are 8-bit integers in float form and quad precision is not supported. The algorithm is otherwise parallel to `k_rem_pio2.c`: convolve chunks with a caller-supplied `2/pi` table, distill into integer chunks, round/complement, recompute on cancellation, multiply by chunked `pi/2`, and compress into output precision.

Dependencies include `scalbnf`, `floorf`, and caller-provided large `2/pi` data.
