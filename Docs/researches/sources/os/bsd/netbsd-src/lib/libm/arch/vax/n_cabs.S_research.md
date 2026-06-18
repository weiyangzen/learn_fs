# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_cabs.S

## Scope

Implements VAX `hypot`, `hypotf`, `hypotl`, compatibility `_cabs`, Fortran `z_abs`, and internal scaled complex absolute value helper `__libm_cdabs_r6`.

## APIs And Behavior

- `_hypotf` promotes float arguments to double, calls `_hypot`, and converts back.
- `_hypot` loads two double arguments and shares `cabs2`.
- `z_abs` accepts a by-reference complex argument for Fortran calling conventions.
- `__libm_cdabs_r6` loads complex components by reference and returns a scaled absolute value for complex square-root support.
- Detects reserved operands and either returns/propagates them or copies original complex parts for internal callers.
- Orders absolute component magnitudes, scales the larger value near a stable exponent, avoids work for zero or negligible smaller component, computes scaled `x*x + y*y`, and jumps into `__libm_dsqrt_r5`.

## Dependencies And Risks

- Depends on `n_sqrt.S` internal `__libm_dsqrt_r5`.
- Preserves a scaling exponent in `%r6`; callers must observe the register protocol.
- Overflow path intentionally halves then doubles to produce meaningful VAX overflow behavior.
