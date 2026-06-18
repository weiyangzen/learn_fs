# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cephes_subr.c

## Scope

Double-precision helper routines derived from Cephes/Moshier for complex trig functions.

## APIs And Behavior

- `_cchsh(x, c, s)` computes `cosh(x)` and `sinh(x)`, using direct functions for `|x| <= 0.5` and `exp` split form otherwise.
- `_redupi(x)` subtracts the nearest integer multiple of pi using split constants `DP1`, `DP2`, `DP3`.
- `_ctans(z)` computes `cosh(2y) - cos(2x)` via a Taylor series, after reducing `2x` modulo pi, for use near tangent denominator cancellation.

## Dependencies And Risks

- `_ctans` loop stops when `fabs(t/d) <= MACHEP`; assumes convergence and nonzero accumulated denominator.
- Split-pi constants determine reduction accuracy.
