# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/invtrig.c

This file defines shared ld80 constants for inverse trigonometric functions.

It provides `pS0..pS6` and `qS1..qS5` for asin/acos approximations, `atanhi[]` and `atanlo[]` for atan argument-reduction constants, `aT[]` for atan polynomial terms, and `pi_lo`.

It contains data only, no executable functions. The coefficient arrays are shorter than ld128’s because ld80 has a smaller mantissa.

Consumers include inverse trig source files that include `invtrig.h`.
