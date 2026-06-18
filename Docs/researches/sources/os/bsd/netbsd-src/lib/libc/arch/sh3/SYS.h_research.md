# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/SYS.h

This header defines SH3 syscall wrapper macros. `SYSTRAP` loads a syscall number from an inline literal into `r0` and uses `trapa #0x80`; wrappers branch to a local `JUMP_CERROR` block on failure.

It supports PIC and non-PIC paths for jumping to `cerror`, and defines `PSEUDO`, `RSYSCALL`, and `WSYSCALL` macro families. It is the common syscall ABI layer for SH3 assembly wrappers.
