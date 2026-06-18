# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_tanpil.c

This file implements `tanpil(long double x)`, computing `tan(pi*x)`.

A private inline `__kernel_tanpil()` multiplies a reduced fractional input by split pi constants and calls `__kernel_tanl`, switching to reciprocal behavior around one-quarter. The public function handles small inputs, half-integers, finite large values, infinities, and NaNs.

For `|x| < 1`, it returns signed small-angle results, infinities at half-integers, and signs based on input. For larger finite values below `2^112`, it splits integer/fractional parts and uses parity to choose signed zero or signed infinity. Above that threshold, values are integral; between `2^112` and `2^113` it still checks even/odd parity with `fmodl`.
