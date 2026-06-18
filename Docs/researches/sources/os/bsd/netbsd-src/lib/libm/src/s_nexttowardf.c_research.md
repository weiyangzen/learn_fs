# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttowardf.c

Implements float `nexttowardf(float x, long double y)`.

Key behavior: supports ports where long double is double by remapping union fields, handles NaNs, equality, zero to signed min-subnormal, one-ulp float stepping, and overflow/underflow.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, and `memset`.

Notable risks: compatibility macros emulate extended fields on no-long-double ports; long-double NaN inspection is representation-specific.
