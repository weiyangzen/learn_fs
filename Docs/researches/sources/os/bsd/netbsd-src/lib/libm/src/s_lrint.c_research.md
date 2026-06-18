# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_lrint.c

Template implementation for `lrint`-family functions. Default instantiation is `lrint(double)`; other files include it after defining macros.

Key behavior: holds the floating-point environment, rounds with `roundit`, casts to integer type, clears spurious `FE_INEXACT` if `FE_INVALID` occurred, then updates the environment.

Important dependencies: `fenv.h`, `math.h`, and template macros `stype`, `roundit`, `dtype`, `fn`.

Notable risks: correctness favors exception semantics over speed.
