# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/cerror.S

This file defines or1k `__cerror`, the shared syscall error handler. In reentrant builds it saves registers and calls `__errno`; in non-reentrant builds it locates global `errno` directly, with PIC and non-PIC address paths.

It stores the error value, then returns `-1` in both `r11` and `r12`. All or1k syscall wrappers depend on this for consistent errno semantics.
