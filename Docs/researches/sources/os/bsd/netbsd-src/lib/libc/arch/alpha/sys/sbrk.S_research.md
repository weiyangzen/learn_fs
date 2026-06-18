# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/sbrk.S

Alpha implementation of `_sbrk` with weak `sbrk`.

Key behavior:
- Exports `__curbrk` initialized to `_end`.
- Loads current break, adds requested increment, and calls kernel `break`.
- Stores the new break into `__curbrk`.
- Returns the old break.

Dependencies:
- Kernel `break` syscall.
- Shared `__curbrk` used by `_brk`.
