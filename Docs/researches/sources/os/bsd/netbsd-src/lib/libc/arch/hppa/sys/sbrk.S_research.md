# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/sbrk.S

This HPPA `sbrk` defines `__curbrk` initialized to `_end`, computes the requested new break from the current value plus increment, invokes `break`, updates `__curbrk`, and returns the old break value.
