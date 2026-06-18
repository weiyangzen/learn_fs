# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/sbrk.S

This IA-64 `sbrk` defines `__curbrk` initialized to `_end`, returns the current break for zero increment, otherwise computes and applies a new break through `break`, updates `__curbrk`, and returns the old value.
