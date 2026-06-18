# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/creal.c

## Scope

Implements `double creal(double complex)`.

## APIs And Behavior

- Wraps input in `double_complex`.
- Returns `REAL_PART(w)`.

## Dependencies And Risks

- Depends on `math_private.h` complex layout helpers.
