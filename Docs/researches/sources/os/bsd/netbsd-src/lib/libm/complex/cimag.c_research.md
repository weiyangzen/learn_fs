# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cimag.c

## Scope

Implements `double cimag(double complex)`.

## APIs And Behavior

- Wraps the complex value in `double_complex` from `math_private.h`.
- Returns `IMAG_PART(w)`.

## Dependencies And Risks

- Depends on NetBSD private complex union layout macros.
