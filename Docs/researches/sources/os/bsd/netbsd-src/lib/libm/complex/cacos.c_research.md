# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacos.c

## Scope

Legacy standalone double complex arccosine implementation derived from Moshier code.

## APIs And Behavior

- Computes `w = casin(z)`.
- Returns `(pi/2 - Re(w)) - Im(w) * I`.

## Dependencies And Risks

- Depends on `casin`, `creal`, and `cimag`.
- The active build may instead get double `cacos` from `catrig.c`; this file remains a simple identity-based implementation.
