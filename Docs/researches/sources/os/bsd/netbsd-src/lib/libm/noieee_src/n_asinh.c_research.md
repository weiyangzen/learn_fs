# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asinh.c

Implements legacy double `asinh()`. It uses `log1p()` identities with different paths for tiny, normal, and very large magnitudes.

Key behavior:
- Returns NaN unchanged on IEEE targets.
- For tiny `|x|`, returns `x`.
- For moderate values, computes `sign(x) * log1p(t + t/(1/t + sqrt(1+(1/t)^2)))`.
- For very large values, computes `sign(x) * (log1p(|x|) + ln2)`.

Important dependencies: `mathimpl.h`, `copysign()`, `sqrt()`, and `log1p()`.

Notable risks:
- Thresholds are legacy constants tuned for VAX/IEEE double behavior.
