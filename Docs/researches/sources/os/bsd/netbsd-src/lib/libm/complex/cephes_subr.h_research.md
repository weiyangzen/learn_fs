# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.h

## Scope

Header declarations for double Cephes complex helpers.

## APIs

- Declares `_cchsh(double, double *, double *)`.
- Declares `_redupi(double)`.
- Declares `_ctans(double complex)`.

## Dependencies And Risks

- Requires including translation units to have `double complex` visible from `<complex.h>`.
