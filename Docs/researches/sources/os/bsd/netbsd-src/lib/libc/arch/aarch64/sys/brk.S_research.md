# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/brk.S

AArch64 implementation of `_brk` with weak `brk`.

Key behavior:
- Defines hidden `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk` up to `__minbrk`.
- Calls the kernel `break` syscall.
- On success stores the requested/clamped break into hidden `__curbrk`.
- Returns zero on success.

Dependencies:
- Shared `__curbrk` from `sbrk.S`.
- `break` syscall and `SYS.h` macros.

Notes:
- Maintains libc’s view of the program break for `sbrk`.
