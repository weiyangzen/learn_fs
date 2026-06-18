# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/csqrt.c

## Scope

Implements `double complex csqrt`.

## APIs And Behavior

- Handles positive-real-axis cases specially, preserving non-negative imaginary zero rules and branch cut behavior for negative zero.
- Handles pure imaginary inputs with equal real/imaginary magnitudes.
- Rescales large inputs by `1/4` and small inputs by `2^54`, then rescales result to avoid internal overflow/underflow.
- Computes magnitude with `cabs` and uses the standard stable branch based on sign of `x`.
- Chooses imaginary sign based on sign of input `y`.

## Dependencies And Risks

- Signed-zero behavior is branch-cut significant.
- Small-input scaling path is enabled with hard-coded powers.
