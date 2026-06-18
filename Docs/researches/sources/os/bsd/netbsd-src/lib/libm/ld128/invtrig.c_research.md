# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/invtrig.c

This file defines shared ld128 constants for inverse trigonometric functions.

For `asinl()` and `acosl()`, it provides polynomial numerator coefficients `pS0..pS9` and denominator coefficients `qS1..qS9`. For `atanl()`, it defines high and low table constants for argument-reduction breakpoints plus the `aT[]` odd/even polynomial coefficient table. It also defines `pi_lo`.

The file contains no public functions. It is data backing for inverse trig implementations that include `invtrig.h`.

The ld128 coefficient sets are longer than the ld80 versions to support 113-bit precision.
