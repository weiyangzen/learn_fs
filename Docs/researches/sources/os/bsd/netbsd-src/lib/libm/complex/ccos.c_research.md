# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ccos.c

## Scope

Implements `double complex ccos`.

## APIs And Behavior

- Calls `_cchsh(cimag(z), &ch, &sh)` for hyperbolic cosine/sine of the imaginary part.
- Returns `cos(x)*cosh(y) - i*sin(x)*sinh(y)`.

## Dependencies And Risks

- Depends on `cephes_subr` helper `_cchsh`.
