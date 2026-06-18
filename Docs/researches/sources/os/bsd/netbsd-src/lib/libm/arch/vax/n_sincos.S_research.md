# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_sincos.S

## Scope

Implements VAX `sin`, `cos`, float wrappers, and long-double aliases using the hidden argument-reduction and polynomial helpers from `n_argred.S`.

## APIs And Behavior

- `_sinf` and `_cosf` promote float arguments to double, call `_sin` / `_cos`, and convert back.
- `_sinl` and `_cosl` strongly alias to `_sin` and `_cos`.
- `_sin` returns zero or reserved operands unchanged; `_cos` returns reserved operands unchanged.
- Saves and clears PSL invalid/floating-underflow bits before argument reduction and restores them afterward.
- Calls `__libm_argred`; passes `%r4 = 0` for sine and `%r4 = 1` for cosine; calls `__libm_sincos` for final polynomial evaluation.

## Dependencies And Risks

- Depends on exact helper register contracts from `n_argred.S`.
- PSL status-bit save/restore is required to avoid exposing internal reduction exceptions.
- Accuracy comments report sub-ulp observed errors on random `[0, 2*pi]` tests.
