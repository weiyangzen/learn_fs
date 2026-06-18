# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cbrt.S

## Scope

Implements VAX cube root for double, float wrapper, long-double alias, and Fortran-style by-reference entry point.

## APIs And Behavior

- `cbrtf` promotes to double and delegates to `cbrt`.
- `cbrtl` weakly aliases to `cbrt`.
- `cbrt` strongly aliases to `d_cbrt`; `dcbrt_` loads the argument by reference.
- Zero and reserved operands return unchanged.
- Extracts and preserves sign, constructs a rough cube-root estimate from exponent/bias arithmetic, refines with single-precision rational steps, then performs a final double-precision Newton-like correction.
- Restores the input sign at return.

## Dependencies And Risks

- Assumes VAX D-format bit layout for exponent rotation and bias arithmetic.
- Accuracy comments claim error below 0.667 ulp.
- Reserved operands are detected by zero biased exponent after masking.
