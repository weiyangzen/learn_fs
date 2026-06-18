# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_tan.S

## Scope

Implements VAX `tan`, `tanf`, and long-double alias using the shared `__libm_argred` / `__libm_sincos` helpers.

## APIs And Behavior

- `_tanl` strongly aliases to `_tan`; public `tan` weakly aliases to `_tan`.
- `_tan` returns zero or reserved operands unchanged.
- Saves and clears PSL invalid/floating-underflow bits around internal computation.
- Performs argument reduction once, saves reduced argument/quadrant state, calls `__libm_sincos` for sine, restores state, calls it again for cosine, and returns `sin/cos`.
- `_tanf` promotes to double and converts back.

## Dependencies And Risks

- Depends on the hidden helper register protocol in `n_argred.S`.
- Division by a very small cosine is left to VAX floating behavior.
- Accuracy comment reports observed max error of about 2.15 ulp.
