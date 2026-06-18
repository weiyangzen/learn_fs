# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_acosh.c

Implements legacy double `acosh()`. It uses stable `log1p()`-based formulas to avoid overflow and cancellation.

Key behavior:
- Returns NaN unchanged on IEEE targets.
- For very large `x`, computes `log1p(x) + ln2`.
- Otherwise computes `log1p(sqrt(x-1) * (sqrt(x-1) + sqrt(x+1)))`.
- Relies on invalid results from `sqrt(x-1)` for `x < 1`.

Important dependencies: `mathimpl.h`, `sqrt()`, and `log1p()`.

Notable risks:
- Domain signaling is mostly delegated to underlying arithmetic rather than explicit checks.
