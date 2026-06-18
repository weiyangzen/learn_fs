# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads `__curbrk` through TOC addressing, adds the increment, calls `break`, stores the new break on success, and returns the old break.

It is the PowerPC64 cached-program-break wrapper paired with `brk.S`.
