# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_gamma.c

Implements legacy `gamma()` returning the gamma function, not log-gamma. It combines rational approximation, Stirling expansion, and reflection for negative inputs.

Key behavior:
- For `x >= 6`, computes a split log-gamma approximation via `large_gam()` and exponentiates with `__exp__D()`.
- For moderate positive values, reduces to a rational approximation around the gamma minimum.
- For very small `x`, returns approximately `1/x`, with zero producing infinity.
- For negative nonintegers, uses the reflection formula with sine/cosine of the fractional distance to the nearest integer.
- Negative integers and overflow return infinity or legacy `infnan()` depending on target.

Important dependencies: `mathimpl.h`, `__log__D()`, `__exp__D()`, `floor()`, `ceil()`, `sin()`, `cos()`, and `M_PI`.

Notable risks:
- Uses global/static endian detection and `TRUNC()` word manipulation for extra-precision splitting.
- Calls `gamma()` recursively in reflection paths.
