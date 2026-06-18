# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanl.c

## Scope

Implements `long double complex ctanl`.

## APIs And Behavior

- Denominator is `cosl(2x) + coshl(2y)`.
- Uses `_ctansl` if denominator magnitude is below `0.25L`.
- Zero denominator returns `LDBL_MAX + LDBL_MAX * I`.
- Returns `sinl(2x)/d + i*sinhl(2y)/d`.

## Dependencies And Risks

- Depends on `cephes_subrl`.
