# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/arith.h

Alpha gdtoa arithmetic configuration.

Key behavior:
- Defines `IEEE_LITTLE_ENDIAN`.
- Defines `Sudden_Underflow` when `_IEEE_FP` is not defined.

Dependencies:
- Alpha floating-point mode macro `_IEEE_FP`.
