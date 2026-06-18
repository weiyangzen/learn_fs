# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/shmat.S

AArch64 syscall stub for `shmat`.

Key behavior:
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`, generating a standard syscall wrapper with error handling and return.

Dependencies:
- Generic syscall macros in `SYS.h`.
