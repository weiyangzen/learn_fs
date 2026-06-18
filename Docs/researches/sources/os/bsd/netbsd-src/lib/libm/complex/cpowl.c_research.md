# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpowl.c

## Scope

Implements `long double complex cpowl`.

## APIs And Behavior

- Long-double polar formula for complex exponentiation.
- Uses `cabsl`, `cargl`, `powl`, `expl`, `logl`, `cosl`, and `sinl`.
- Zero base returns complex zero.

## Dependencies And Risks

- Does not implement extensive C99 complex pow special cases.
