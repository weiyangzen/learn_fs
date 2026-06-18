# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sincos.c

Implements double `sincos(x, &sin, &cos)` by combining sine and cosine range reduction.

Key behavior: uses a small-input path that returns `sin=x`, `cos=1` while generating inexact as needed; handles Inf/NaN by setting both outputs to NaN; dispatches quadrant mappings with `__kernel_sincos()`.

Important dependencies: `namespace.h`, `math_private.h`, `k_sincos.h`, and `__ieee754_rem_pio2`.

Notable risks: output pointer order is swapped in odd quadrants; sign fixups are easy to regress.
