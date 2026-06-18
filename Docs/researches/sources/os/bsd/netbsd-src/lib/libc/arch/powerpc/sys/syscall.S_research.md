# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/syscall.S

This file contains only a comment that `syscall` is aliased to `__syscall`. The implementation and aliases live in `__syscall.S`.

It prevents duplicate implementation while preserving the expected source layout.
