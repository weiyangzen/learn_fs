# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanhf.c

## Scope

Implements `float complex ctanhf`.

## APIs And Behavior

- Float version of `sinh(2x)/(cosh(2x)+cos(2y)) + i*sin(2y)/d`.

## Dependencies And Risks

- Direct formula.
