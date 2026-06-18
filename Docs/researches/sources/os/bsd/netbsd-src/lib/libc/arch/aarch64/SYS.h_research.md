# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/SYS.h

AArch64 assembly macro header for libc syscall stubs.

Key behavior:
- Includes `<machine/asm.h>` and `<sys/syscall.h>`.
- Defines `SYSTRAP(x)` as `svc #(SYS_x)`.
- Provides `_SYSCALL_NOERROR`, `_SYSCALL`, `SYSCALL`, `PSEUDO`, `RSYSCALL`, and weak syscall macros.
- `_INVOKE_CERROR` branches to `__cerror` on carry-condition error.
- Declares hidden/global `__cerror`.

Dependencies:
- AArch64 condition-code convention after `svc`.
- NetBSD assembler entry macros.

Notes:
- This header is the shared ABI contract for AArch64 syscall assembly files.
