# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_ilogb.c

Implements `ilogb()` and `ilogbf()`, plus an `ilogbl` alias when long double is not distinct.

Key behavior:
- Returns `FP_ILOGB0` for zero.
- Returns `FP_ILOGBNAN` for NaN.
- Returns `INT_MAX` for infinities.
- Otherwise casts `logb(x)` to `int`.
- `ilogbf()` delegates to double `ilogb()`.

Important dependencies: `math.h`, `logb()`, `finite()`, and strong aliases.

Notable risks:
- Finite nonzero behavior depends on `logb()` being available and correct for the target format.
