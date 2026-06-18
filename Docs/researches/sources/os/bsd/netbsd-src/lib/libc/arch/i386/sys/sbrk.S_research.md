# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/sbrk.S

This i386 `sbrk` defines `__curbrk` initialized to `_end`. It returns the current break immediately for zero increment; otherwise it computes a new break, invokes `break`, updates `__curbrk`, and returns the old value.
