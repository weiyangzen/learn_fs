# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/clog.c

## Scope

Implements `double complex clog`.

## APIs And Behavior

- Computes magnitude with `cabs(z)`.
- Real part is `log(|z|)`.
- Imaginary part is `atan2(Im(z), Re(z))`.

## Dependencies And Risks

- Delegates scaling to `cabs`; branch cut follows `atan2`.
