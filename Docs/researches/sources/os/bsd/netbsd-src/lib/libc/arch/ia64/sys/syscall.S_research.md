# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/syscall.S

IA-64 generic `syscall` wrapper.

Key points:
- Includes `SYS.h`.
- Defines weak public `syscall` around `_syscall` via `WSYSCALL(syscall,_syscall)`.
