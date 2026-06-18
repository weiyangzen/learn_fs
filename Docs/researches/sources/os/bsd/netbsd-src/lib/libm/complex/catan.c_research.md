# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catan.c

## Scope

Legacy standalone double complex arctangent implementation.

## APIs And Behavior

- Defines weak alias `catan -> _catan`.
- Computes real part as reduced `0.5 * atan2(2x, 1 - x^2 - y^2)`.
- Computes imaginary part as `0.25 * log(((x^2 + (y+1)^2) / (x^2 + (y-1)^2)))`.
- Uses `_redupi` to keep the real part reduced.
- Overflow/error path returns `DBL_MAX + DBL_MAX * I`.

## Dependencies And Risks

- Depends on `cephes_subr.h`.
- Singularities at `x == 0, y > 1`, zero denominators, and exact branch cases use the coarse overflow return.
