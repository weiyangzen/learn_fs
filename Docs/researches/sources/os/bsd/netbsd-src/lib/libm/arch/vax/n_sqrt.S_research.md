# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sqrt.S

## Scope

Implements VAX `sqrt`, `sqrtf`, long-double aliases, by-reference `d_sqrt`, and hidden internal helper `__libm_dsqrt_r5`.

## APIs And Behavior

- `sqrtl` / `_sqrtl` weakly alias to `sqrt`.
- `d_sqrt` loads a double by reference; `sqrt` loads by value.
- Zero and reserved operands return unchanged.
- Positive inputs enter `__libm_dsqrt_r5_lcl`, which forms a magic initial approximation, runs two Heron iterations, rescales the argument to avoid overflow/underflow, then applies a cubic refinement formula.
- Negative nonzero input calls `infnan(EDOM)` to generate a reserved-operand fault.
- `sqrtf` promotes to double and converts the result back.

## Dependencies And Risks

- `__libm_dsqrt_r5` is an internal target for `n_cabs.S`; the exported symbol has two `halt` instructions before the local entry to enforce call discipline.
- Requires VAX exponent encoding and D-format scaling semantics.
- Error behavior is VAX reserved-operand style.
