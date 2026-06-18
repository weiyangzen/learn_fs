# File Research: sources/os/plan9/plan9/sys/src/cmd/map/sqrt.c

Provides a local floating-point `sqrt()` implementation using Newton iteration.

Behavior:
- Returns `0` for negative or zero input.
- Uses `frexp()` to derive initial mantissa/exponent scaling.
- Adjusts exponent to be even, scales initial estimate with powers of `1L<<30`, then performs five Newton updates.

Notes:
- Comment says it will not work on one’s-complement machines.
- This is an old portability support file for environments lacking suitable math library behavior.
