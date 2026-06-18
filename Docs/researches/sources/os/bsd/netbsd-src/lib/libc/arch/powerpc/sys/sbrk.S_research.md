# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads hidden `__curbrk`, adds the requested increment, calls kernel `break`, stores the new break on success, and returns the old break.

It has PIC and non-PIC addressing paths. It is paired with `brk.S` and shares the same cached break invariant.
