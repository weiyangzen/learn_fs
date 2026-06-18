# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhl.c

## Scope

Implements `long double complex ctanhl`.

## APIs And Behavior

- Uses `coshl`, `cosl`, `sinhl`, and `sinl`.
- Returns long-double complex hyperbolic tangent formula.

## Dependencies And Risks

- Direct formula can overflow for large real components.
