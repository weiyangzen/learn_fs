# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/ptrace.S

This HPPA `ptrace` wrapper first calls `__cerror` with a zero error code to clear `errno`, preserving arguments and PIC state around that call. It then invokes the actual `ptrace` syscall so callers can distinguish a valid `-1` result from an error by checking `errno`.
