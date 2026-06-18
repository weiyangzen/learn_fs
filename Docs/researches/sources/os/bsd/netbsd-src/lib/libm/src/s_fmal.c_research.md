# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmal.c

Implements software long-double `fmal()` using doubled long-double precision arithmetic.

Key behavior: mirrors `s_fma.c`: handles special values, scales operands, uses Dekker splitting, adjusts sticky bits with `nextafterl`, restores original rounding, and handles subnormal output carefully.

Important dependencies: `fenv.h`, `<machine/ieee.h>`, `frexpl`, `ldexpl`, `ilogbl`, `nextafterl`, `copysignl`, and `math_private.h`.

Notable risks: `add_and_denormalize()` returns through `ldexp((double)sum.hi, scale)`, so representation assumptions and precision behavior are especially sensitive.
