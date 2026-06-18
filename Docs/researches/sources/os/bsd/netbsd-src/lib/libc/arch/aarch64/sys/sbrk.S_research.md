# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/sbrk.S

AArch64 implementation of `_sbrk` with weak `sbrk`.

Key behavior:
- Defines hidden `__curbrk` initialized to `_end`.
- Loads current break, adds the requested increment, and calls the kernel `break` syscall.
- On success stores the new break into `__curbrk`.
- Returns the old break value.

Dependencies:
- Shared use of `__curbrk` with `brk.S`.
- Kernel `break` syscall.

Notes:
- The source’s `.size` directive names `_end`, which looks unusual because the object being defined is `__curbrk`.
