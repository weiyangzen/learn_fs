# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_lgammal_r.c

This file implements `lgammal_r(long double x, int *signgamp)` for 80-bit extended precision.

It has the same overall structure as the ld128 version but uses shorter coefficient sets and ld80 bit extraction. Negative inputs use a local `sin_pil()` helper with 63/61-bit rounding thresholds and `__kernel_sinl`/`__kernel_cosl`.

Positive inputs are split into domains below 2, between 2 and 8, and large values. It uses polynomial approximations around 1, 2, and `tc`, recurrence products for `x < 8`, and Stirling expansion for larger inputs.

The function uses `ENTERI`/`RETURNI` to preserve floating-point environment behavior, unlike the ld128 version which directly returns in many paths.
