# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammaf_r.c

This file is the float implementation of reentrant logarithmic gamma, `__ieee754_lgammaf_r(float x, int *signgamp)`.

It follows the same fdlibm structure as the double version: reflection for negative non-integers via `sin_pif()`, exact singular handling for zero and negative integers, polynomial approximations near the gamma minimum and around `[1,2]`, recurrence for `[2,8)`, and a Stirling expansion for larger finite inputs.

The coefficient tables and thresholds are float-specific. Dependencies include `floorf`, `fabsf`, `__ieee754_logf`, `__kernel_sinf`, `__kernel_cosf`, and float word extraction macros.
