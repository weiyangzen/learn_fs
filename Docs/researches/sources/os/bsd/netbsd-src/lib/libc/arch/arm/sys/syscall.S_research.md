# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/syscall.S

ARM generic `syscall` wrapper.

Key points:
- Includes `SYS.h`.
- Uses `WSYSCALL(syscall,_syscall)` so public `syscall` weak-aliases the private `_syscall` entry.
