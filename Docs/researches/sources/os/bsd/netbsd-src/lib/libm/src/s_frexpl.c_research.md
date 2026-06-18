# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpl.c

Implements long-double `frexpl()` for supported extended formats.

Key behavior: returns zero/subnormal, normal, Inf, and NaN through exponent-field inspection; scales subnormals by `2^514`; sets normal mantissa exponent to bias-1.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `LDBL_MAX_EXP == 0x4000`.

Notable risks: value of `*ex` is left unspecified for Inf/NaN, matching source comments; only supported long-double exponent layout is accepted.
