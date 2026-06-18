# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cexpf.c

## Scope

Implements `float complex cexpf`.

## APIs And Behavior

- Float version of `exp(x) * (cos(y) + i sin(y))`.

## Dependencies And Risks

- Direct formula; special cases follow real float functions.
