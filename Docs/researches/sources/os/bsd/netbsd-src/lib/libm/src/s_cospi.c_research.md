# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospi.c

Implements double `cospi(x)`, computing `cos(pi*x)` with period-aware reduction in units of `x` rather than multiplying by pi for all cases.

Key behavior: handles small values, half-integers, integer parity, Inf/NaN invalid results, and very large integral inputs. Uses `FFLOOR` for `1 <= |x| < 2^52`.

Important dependencies: `k_cospi.h`, `k_sinpi.h`, `math_private.h`, and `copysign`-style bit handling.

Notable risks: parity recovery for large finite values is subtle; exact half-integer handling is required for zero results.
