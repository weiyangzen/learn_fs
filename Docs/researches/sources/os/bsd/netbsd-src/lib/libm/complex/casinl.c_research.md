# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casinl.c

## Scope

Long-double complex arcsine implementation.

## APIs And Behavior

- Defines weak alias `casinl -> _casinl`.
- Uses the Moshier identity `-i * clogl(i*z + csqrtl(1 - z*z))`.
- Manually computes `z*z` from real and imaginary parts.
- Leaves old real-domain and power-series code disabled.

## Dependencies And Risks

- Depends on `csqrtl` and `clogl`.
- Long-double inverse trig may be aliased in `catrigl.c` depending on build configuration.
