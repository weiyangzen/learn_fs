# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/catrigf.c

## Scope

Float version of the modern inverse complex trig implementation for `casinhf`, `casinf`, `cacosf`, `cacoshf`, `catanhf`, and `catanf`.

## APIs And Behavior

- Defines weak aliases for `casinf` and `catanf`.
- Mirrors `catrig.c` with float constants, `CMPLXF`, `hypotf`, `sqrtf`, `atan2f`, `logf`, and `log1pf`.
- Uses `do_hard_work` to stabilize `casinhf` / `cacosf` near branch cuts.
- Handles NaN/Inf, zero, small inputs, large inputs, and inexact raising.
- Implements `catanhf` with stable `log1pf` and `atan2f` formulas; `catanf` reverses through `catanhf`.

## Dependencies And Risks

- Depends on `math_private.h` float word macros for reciprocal scaling.
- Precision thresholds are float-specific and must match `FLT_EPSILON` and exponent range.
