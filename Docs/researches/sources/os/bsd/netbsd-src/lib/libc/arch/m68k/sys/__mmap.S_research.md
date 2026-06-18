# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__mmap.S

This file defines the internal `__mmap` syscall wrapper around kernel `mmap`. It uses `_SYSCALL(__mmap,mmap)`, then returns directly, copying `%d0` to `%a0` for the SVR4 ABI variant.

It is simple syscall ABI glue. The only behavioral detail beyond standard error handling is the pointer-return register accommodation under `__SVR4_ABI__`.
