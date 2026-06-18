# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/fork.S

Alpha wrapper for `__fork`.

Key behavior:
- Calls kernel `fork` with common error handling.
- Uses `cmovne a4, zero, v0` to return zero in the child and child pid in the parent.
- Returns to caller.

Dependencies:
- Alpha fork return convention using `a4`.
