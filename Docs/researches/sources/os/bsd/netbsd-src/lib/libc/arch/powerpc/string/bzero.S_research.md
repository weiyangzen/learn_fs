# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/bzero.S

This file implements PowerPC `bzero` and `memset`. `bzero` sets the fill value to zero and branches into the shared fill path; `memset` expands the byte fill value across a word and uses simple or cache-aware loops.

For zero fills, non-kernel builds read `_libc_powerpc_cache_info` to obtain data-cache line size and can use `dcbz` to clear cache blocks efficiently. The fallback path aligns to word boundaries, fills words, then clears remaining bytes. Correctness depends on preserving the original destination pointer for `memset` return and safely handling unknown cache info.
