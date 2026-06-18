# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_lround.c

Implements no-IEEE `lround(double)`.

Key behavior:
- Rounds halfway cases away from zero.
- Uses `ceil(x)` for positive values and `ceil(-x)` for negative values.
- Converts the intermediate result to `long`.

Notable risk:
- There is no explicit overflow handling before converting to `long`; behavior follows the platform conversion semantics.
