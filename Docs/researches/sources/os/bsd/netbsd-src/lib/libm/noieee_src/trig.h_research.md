# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/trig.h

Defines no-IEEE trigonometric constants, exported common constants, and polynomial kernels for `sin`, `cos`, and `tan`.

Key contents:
- Pi-related constants `PIo4`, `PIo2`, `PI3o4`, `PI`, and `PI2`, plus `thresh`.
- Shared constants `__zero`, `__one`, `__negone`, `__half`, `__small`, and `__big`.
- `sin__S(z)` macro approximates `(sin(x)-x)/x` on the primary interval.
- `cos__C(z)` macro approximates `cos(x)-1+x*x/2`.
- Uses different coefficient counts for VAX/Tahoe versus IEEE-style targets.
- Uses `vc`, `ic`, and optional `vccast` macros supplied by `mathimpl.h`.

This header is not just declarations; including it with `_LIBM_DECLARE` emits storage for shared constants.
