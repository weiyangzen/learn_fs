# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__sigtramp2.S

This HPPA signal trampoline declares unwind metadata for the signal frame and returns from signal delivery by invoking `setcontext` with the saved user context. If returning from `setcontext` fails, it exits through the syscall path.
