# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/brk.S

This file implements `_brk` with weak alias `brk`. It defines hidden `__minbrk` and `__curbrk` initialized to `_end`, clamps the requested break with an unsigned comparison, calls the `break` syscall, stores the new break into `__curbrk` on success, returns zero, and jumps to `__cerror` on failure.

It uses RISC-V `lla` and pointer-width macros for symbol and data access. The cached break update is the key libc-side state.
