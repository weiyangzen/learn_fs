# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccoshf.c

## Scope

Implements `float complex ccoshf`.

## APIs And Behavior

- Float version of `cosh(x)*cos(y) + i*sinh(x)*sin(y)`.

## Dependencies And Risks

- Direct formula inherits float overflow and special handling from real functions.
