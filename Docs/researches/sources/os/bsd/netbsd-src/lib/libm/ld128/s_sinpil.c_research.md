# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_sinpil.c

This file implements `sinpil(long double x)`, computing `sin(pi*x)`.

It handles small `|x|` with direct split-pi multiplication, preserving signed zero. For `|x| < 1`, it dispatches by quadrant to `__kernel_sinpil` or `__kernel_cospil`. For larger finite inputs below `2^112`, it splits integer and fractional parts with `FFLOORL128`, evaluates the fractional quadrant, and flips sign using integer parity.

Inf/NaN returns NaN. For `|x| >= 2^112`, every representable value is an integer, so it returns signed zero.

The function is designed to avoid the range-reduction error that would occur with `sinl(pi*x)` for large or special pi-multiple inputs.
