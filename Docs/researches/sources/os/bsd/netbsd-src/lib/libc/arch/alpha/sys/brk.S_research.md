# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/brk.S

Alpha implementation of `_brk` with weak `brk`.

Key behavior:
- Imports `__curbrk` and exports `__minbrk` initialized to `_end`.
- Clamps requested break to at least `__minbrk`.
- Calls kernel `break`.
- Stores the successful break into `__curbrk`.
- Returns zero on success.

Dependencies:
- Shared `__curbrk` from `sbrk.S`.
- Alpha `break` syscall path.
