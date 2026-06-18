# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/trapezoidal.c

Implements trapezoidal projection.

Key behavior:
- `trapezoidal(par0, par1)` falls back to `rectangular(par0)` when absolute standard parallels are nearly equal.
- Computes slope `k` either from sine for equal parallels or from cosine/latitude differences.
- Computes equator offset `yeq`.
- `Xtrapezoidal()` maps `y = yeq + lat`, `x = y*k*lon`.

Always returns `1`; no clipping is performed.
