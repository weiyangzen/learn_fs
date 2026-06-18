# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cpowf.c

## Scope

Implements `float complex cpowf`.

## APIs And Behavior

- Float version of polar `a^z`.
- Uses `cabsf`, `cargf`, `powf`, `expf`, `logf`, `cosf`, and `sinf`.

## Dependencies And Risks

- Same limited special-case handling as double version.
