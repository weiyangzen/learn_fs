# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxf.c

Implements float `fmaxf()` with explicit NaN and signed-zero behavior.

Key behavior: suppresses spurious exceptions by inspecting NaNs before comparison; returns positive zero when comparing `+0` and `-0`.

Important dependencies: `<machine/ieee.h>` and `union ieee_single_u`.

Notable risks: field layout is target-specific.
