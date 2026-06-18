# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIg.c

Purpose: Generic interval parser used by `strtoI*` wrappers.

Core behavior:
- Calls `strtodg` with the caller's `FPI` to produce one rounded result.
- If the parse is exact, returns only one endpoint.
- If inexact low, increments the significand to form the upper adjacent endpoint.
- If inexact high, decrements or clamps to form the lower adjacent endpoint.
- Handles zero, denormal, normal, infinity, sudden-underflow, exponent-boundary, and sign-order cases.
- Orders interval endpoints according to sign so output `[0]` is the lower bound.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `Balloc`, `Bcopy`, `increment`, `decrement`, `set_ones`, `lshift`, and `rshift`.
