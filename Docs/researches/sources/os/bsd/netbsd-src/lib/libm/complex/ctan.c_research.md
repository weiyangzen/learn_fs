# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/ctan.c

## Scope

Implements `double complex ctan`.

## APIs And Behavior

- Denominator is `cos(2x) + cosh(2y)`.
- If denominator magnitude is below `0.25`, recomputes it with `_ctans` Taylor helper.
- If denominator is zero, returns `DBL_MAX + DBL_MAX * I`.
- Otherwise returns `sin(2x)/d + i*sinh(2y)/d`.

## Dependencies And Risks

- Depends on `cephes_subr`.
- Large `y` may overflow through `cosh` / `sinh`.
