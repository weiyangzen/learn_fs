# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/SYS.h

Alpha assembly macro header for libc syscall stubs.

Key behavior:
- Includes `<machine/asm.h>` and `<sys/syscall.h>`.
- Defines `CALLSYS_ERROR` around `CALLSYS_NOERROR`, GP setup, `a3` error-result testing, and branch to `__cerror`.
- Provides `SYSCALL`, `SYSCALL_NOERROR`, `PSEUDO`, `PSEUDO_NOERROR`, `RSYSCALL`, `RSYSCALL_NOERROR`, and `WSYSCALL`.
- Uses Alpha `LEAF`, `RET`, and `END` macros.

Dependencies:
- Alpha syscall ABI, where `a3` indicates error.
- NetBSD assembler macro definitions.
