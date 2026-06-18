# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/cacoshf.c

## Scope

Legacy standalone float complex inverse hyperbolic cosine implementation.

## APIs And Behavior

- Uses `clogf(z + csqrtf(z + 1) * csqrtf(z - 1))`.
- Leaves disabled identity form documenting why it is not used.

## Dependencies And Risks

- Principal value depends on `csqrtf` branch behavior.
