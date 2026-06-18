# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/shmat.S

Alpha syscall stub for `shmat`.

Key behavior:
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`, generating a standard syscall wrapper with common error handling and return.

Dependencies:
- Alpha syscall macros in `SYS.h`.
