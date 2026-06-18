# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.h

## Scope

Header declarations for float Cephes complex helpers.

## APIs

- Declares `_cchshf(float, float *, float *)`.
- Declares `_redupif(float)`.
- Declares `_ctansf(float complex)`.

## Dependencies And Risks

- Requires `<complex.h>` before or in users for `float complex`.
