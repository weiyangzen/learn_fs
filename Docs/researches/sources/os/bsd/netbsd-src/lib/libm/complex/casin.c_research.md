# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/casin.c

## Scope

Legacy standalone double complex arcsine implementation derived from Moshier code.

## APIs And Behavior

- Defines weak alias `casin -> _casin`.
- Extracts `x` and `y`, leaves old real-domain and power-series code disabled.
- Forms `z*z` manually as `(x-y)*(x+y) + 2xy*i`, computes `sqrt(1 - z*z)`, then `clog(i*z + sqrt(...))`.
- Multiplies by `-i` to implement `asin(z)`.

## Dependencies And Risks

- Depends on `csqrt`, `clog`, and correct branch behavior.
- Active builds may use the more robust `catrig.c` implementation for double `casin`.
