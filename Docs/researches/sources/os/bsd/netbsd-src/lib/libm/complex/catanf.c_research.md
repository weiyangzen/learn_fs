# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catanf.c

## Scope

Legacy standalone float complex arctangent implementation.

## APIs And Behavior

- Defines weak alias `catanf -> _catanf`.
- Float version of the `atan2/log` arctangent formula.
- Uses `_redupif` for real-part reduction.
- Overflow path returns `FLT_MAX + FLT_MAX * I`.

## Dependencies And Risks

- Depends on `cephes_subrf.h`.
- Active build may use `catrigf.c` instead.
