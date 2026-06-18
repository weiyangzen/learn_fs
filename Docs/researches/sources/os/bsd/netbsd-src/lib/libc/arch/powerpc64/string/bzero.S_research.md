# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/bzero.S

This file implements PowerPC64 `bzero` and `memset`. `bzero` maps to `memset` with fill value zero; `memset` uses a byte loop for short or unaligned cases, constructs a repeated 64-bit fill word, and uses unrolled `std` stores for larger aligned spans.

It returns the original destination pointer for `memset`. Unlike the 32-bit PowerPC version, it does not use cache-line `dcbz`; it optimizes through 8-byte and 32-byte store loops.
