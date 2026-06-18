# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterf.c

Implements float `nextafterf(x,y)` by stepping the 32-bit representation toward `y`.

Key behavior: handles NaNs, equality, signed zero to min-subnormal, overflow, and underflow.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes monotonic ordering properties of IEEE float bit patterns with sign-aware branches.
