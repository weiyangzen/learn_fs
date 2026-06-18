# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctanf.c

## Scope

Implements `float complex ctanf`.

## APIs And Behavior

- Float version of complex tangent formula.
- Uses `_ctansf` when the denominator is near cancellation.
- Zero denominator returns `FLT_MAX + FLT_MAX * I`.

## Dependencies And Risks

- Depends on `cephes_subrf`.
