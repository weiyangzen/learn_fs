# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshl.c

## Scope

Implements `long double complex ccoshl`.

## APIs And Behavior

- Uses `coshl`, `cosl`, `sinhl`, and `sinl`.
- Returns `cosh(x)*cos(y) + i*sinh(x)*sin(y)`.

## Dependencies And Risks

- Direct long-double formula; overflow behavior follows real long-double functions.
