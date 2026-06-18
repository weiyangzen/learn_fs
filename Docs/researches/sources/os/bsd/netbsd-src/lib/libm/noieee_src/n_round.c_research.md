# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_round.c

Implements no-IEEE `round(double)` and aliases `roundl` to `round`.

Key behavior:
- Uses `ceil(x)` for positive values and `ceil(-x)` for negative values.
- Adjusts down by one when the distance from the ceiling exceeds `0.5`.
- Rounds halfway cases away from zero.

The implementation is simple and inherits NaN/infinity behavior from `ceil`.
