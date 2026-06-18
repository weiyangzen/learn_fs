# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexpl.c

## Scope

Implements `long double complex cexpl`.

## APIs And Behavior

- Uses `expl`, `cosl`, and `sinl`.
- Returns `exp(x) * (cos(y) + i sin(y))`.

## Dependencies And Risks

- Direct formula inherits long-double overflow behavior.
