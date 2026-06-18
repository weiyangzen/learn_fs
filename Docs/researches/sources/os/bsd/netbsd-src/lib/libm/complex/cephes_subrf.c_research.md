# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subrf.c

## Scope

Float helper routines for complex trigonometric functions.

## APIs And Behavior

- `_cchshf` computes `coshf` and `sinhf`, switching to `expf`-based split form for `|x| > 0.5`.
- `_redupif` reduces by nearest multiple of pi using float-oriented split constants.
- `_ctansf` evaluates the Taylor series for `cosh(2y) - cos(2x)` near tangent denominator cancellation.

## Dependencies And Risks

- Uses `MACHEPF` tolerance.
- Reduction constants are lower precision than the double version, by design.
