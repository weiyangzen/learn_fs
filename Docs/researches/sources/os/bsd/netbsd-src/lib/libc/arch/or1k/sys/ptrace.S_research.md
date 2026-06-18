# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/ptrace.S

This file implements or1k `ptrace` with errno pre-clearing. Reentrant builds save call registers and use `__errno`; non-reentrant builds locate global `errno`, then the wrapper clears it before issuing the `ptrace` syscall.

The pre-clear is needed because `ptrace` may legitimately return `-1` on success. The file is sensitive to PIC register setup and has a typo-like `lwz` instruction spelling in the PIC non-reentrant path as written, which would be build-toolchain dependent.
