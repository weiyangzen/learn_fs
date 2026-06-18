# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_log1pf.c

Implements float `log1pf(x)` with the same FDLIBM structure as double `log1p()`.

Key behavior: handles domain errors, `-1`, Inf/NaN, tiny inputs, rounded `1+x` correction, and polynomial reconstruction with split float `ln2`.

Important dependencies: `namespace.h`, `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: coefficient and threshold choices are float-specific.
