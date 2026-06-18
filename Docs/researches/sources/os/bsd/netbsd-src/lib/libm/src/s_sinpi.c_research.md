# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpi.c

Implements double `sinpi(x)`, computing `sin(pi*x)` with direct period-aware reduction.

Key behavior: preserves signed zero, uses split pi for tiny inputs, evaluates kernels for fractional ranges, strips integer parts with `FFLOOR`, flips sign by integer parity, returns signed zero for large integral values, and invalid NaN for Inf/NaN.

Important dependencies: `k_cospi.h`, `k_sinpi.h`, `math_private.h`, `copysign`, and `FFLOOR`.

Notable risks: tiny-input split-pi path and parity handling are precision-critical.
