# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fabs.c

Implements double `fabs()` by clearing the sign bit in the high word.

Key behavior: preserves NaN payloads and all magnitude bits. Aliases `fabsl` to `fabs` when long double is absent.

Important dependencies: `math_private.h`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double bit layout.
