# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csinhl.c

## Scope

Implements `long double complex csinhl`.

## APIs And Behavior

- Uses `sinhl`, `cosl`, `coshl`, and `sinl`.
- Returns `sinh(x)*cos(y) + i*cosh(x)*sin(y)`.

## Dependencies And Risks

- Direct formula inherits long-double real function behavior.
