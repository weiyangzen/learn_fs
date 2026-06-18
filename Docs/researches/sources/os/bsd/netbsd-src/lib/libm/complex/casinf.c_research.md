# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinf.c

## Scope

Legacy standalone float complex arcsine implementation.

## APIs And Behavior

- Defines weak alias `casinf -> _casinf`.
- Uses the same identity as `casin`: `-i * clog(i*z + sqrt(1 - z*z))`, with float functions and constants.
- Leaves old real-domain and power-series code disabled.

## Dependencies And Risks

- Depends on `csqrtf` and `clogf`.
- Active build may use `catrigf.c` for float inverse trig symbols.
