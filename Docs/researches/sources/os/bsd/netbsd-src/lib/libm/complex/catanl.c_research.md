# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanl.c

## Scope

Long-double complex arctangent implementation.

## APIs And Behavior

- Defines weak alias `catanl -> _catanl`.
- Uses long-double version of `0.5*atan2` real component and `0.25*log` imaginary component formula.
- Reduces real part with `_redupil`.
- Overflow path returns `LDBL_MAX + LDBL_MAX * I`.

## Dependencies And Risks

- Depends on `cephes_subrl.h`.
- Singularities are handled by a coarse max-value fallback.
