# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cospil.c

This file implements `cospil(long double x)`, computing `cos(pi*x)`.

It uses split high/low pi constants with 169-bit approximation comments. For `|x| <= 1`, it dispatches to sine or cosine pi kernels based on the quadrant. For larger finite values below `2^112`, it splits off the integer part with `FFLOORL128`, evaluates the fractional part, and flips sign based on integer parity.

For very large finite inputs, the code relies on long-double integer spacing: `|x| >= 2^113` is always an even integer, so the answer is `1`; between `2^112` and `2^113`, it uses `fmodl(ax, 2)` to determine parity. Inf/NaN returns NaN through volatile zero.
