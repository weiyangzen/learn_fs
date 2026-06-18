# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csin.c

## Scope

Implements `double complex csin`.

## APIs And Behavior

- Calls `_cchsh` for imaginary-part hyperbolic functions.
- Returns `sin(x)*cosh(y) + i*cos(x)*sinh(y)`.

## Dependencies And Risks

- Depends on `cephes_subr`.
