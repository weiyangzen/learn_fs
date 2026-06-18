# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/syscall.S

HPPA generic `syscall` wrapper.

Key points:
- Includes `SYS.h`.
- Uses `WSYSCALL(syscall,_syscall)` to expose public `syscall` as a weak wrapper for `_syscall`.
