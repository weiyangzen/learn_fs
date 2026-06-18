# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_neta.c

Implements `inet_neta`, formatting a `u_long` network number into dotted presentation format.

Behavior:
- Special-cases zero as `"0.0.0.0"`.
- Emits significant high-order bytes separated by dots.
- Uses `snprintf` and explicit buffer-end checks.
- Returns `NULL` with `EMSGSIZE` if output does not fit.

Input format expectations match `inet_network`.
