# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_jn.c

Implements integer-order Bessel functions `jn(int n, double x)` and `yn(int n, double x)`. It builds on `j0/j1` and `y0/y1`, using recurrence and asymptotic shortcuts.

Key behavior:
- Handles negative `n` using parity identities.
- `jn()` delegates to `j0()`/`j1()` for orders 0 and 1.
- If `n <= x`, `jn()` uses forward recurrence from `j0()` and `j1()`.
- If `n > x`, it uses a continued-fraction estimate and backward recurrence, scaling intermediate values to avoid overflow.
- Tiny `x` uses the first Taylor term `(x/2)^n / n!` with underflow cutoff.
- `yn()` uses forward recurrence for all `n > 1`, starting from `y0()` and `y1()`.
- Very large `x` uses direct asymptotic sine/cosine phase patterns.

Important dependencies: `mathimpl.h`, `j0()`, `j1()`, `y0()`, `y1()`, `sin()`, `cos()`, `sqrt()`, `log()`, `fabs()`, `finite()`, and optional `snan()`.

Notable risks:
- Backward recurrence has scaling heuristics (`BMAX`) and a continued-fraction stopping threshold tuned for double precision.
- The loop in `yn()` appears to continue while `!finite(b)`, matching legacy code but worth treating cautiously in maintenance.
