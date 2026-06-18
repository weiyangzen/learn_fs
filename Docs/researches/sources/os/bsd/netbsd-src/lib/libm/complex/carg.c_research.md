# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/carg.c

## Scope

C99 `double carg(double complex)` implementation.

## APIs And Behavior

- Returns `atan2(cimag(z), creal(z))`.

## Dependencies And Risks

- Delegates signed-zero and quadrant semantics to `atan2`.
