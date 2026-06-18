# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/SYS.h

This IA-64 syscall header defines return and wrapper macros around `CALLSYS_NOERROR`. Error-aware wrappers compare `r10` against zero and branch to `__cerror` on failure; pseudo, raw, no-error, and weak syscall macros are provided.
