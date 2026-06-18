# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_log__L.c

Provides the no-IEEE internal polynomial kernel `__log__L(double z)` used by `log1p`, `log`, and `pow`-related code.

Key behavior:
- Approximates `(log(1+x) - 2s) / s` where `z = s*s` and `s = x/(2+x)`.
- Uses Remez-derived coefficients `L1` through `L8` for VAX/Tahoe and `L1` through `L7` for IEEE-style builds.
- Coefficients are declared through `vc` and `ic` macros from `mathimpl.h`.

This file has no public entry point; it is an internal accuracy helper.
