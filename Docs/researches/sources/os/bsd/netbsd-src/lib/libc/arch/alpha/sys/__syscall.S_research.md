# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__syscall.S

Alpha standard wrapper for `__syscall`.

Key behavior:
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`, producing a syscall wrapper with common error handling and return.

Dependencies:
- Alpha syscall macros in `SYS.h`.
