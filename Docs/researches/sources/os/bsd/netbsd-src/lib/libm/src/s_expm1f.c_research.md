# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expm1f.c

Implements float `expm1f(x)` as a float adaptation of `s_expm1.c`.

Key behavior: filters overflow/underflow and nonfinite inputs, reduces by split `ln2`, evaluates the scaled polynomial, and reconstructs using float exponent manipulation.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: thresholds and scaling cases are float-specific; exception behavior relies on `huge` and `tiny`.
