# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/syscall.S

This Alpha syscall wrapper includes `SYS.h` and uses `WSYSCALL(syscall,_syscall)` to expose the weak public `syscall` name backed by `_syscall`. All trap/error behavior is delegated to the Alpha `SYS.h` syscall macro layer.
