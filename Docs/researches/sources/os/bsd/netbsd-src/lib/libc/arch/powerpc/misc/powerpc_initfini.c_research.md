# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/misc/powerpc_initfini.c

This C file defines hidden global `_libc_powerpc_cache_info` and a constructor `_libc_cache_info_init`. At load time, the constructor calls `sysctl` with `CTL_MACHDEP, CPU_CACHEINFO` to populate cache-size/line-size information, guarded by a static `initialized` flag.

The cached data is used by optimized PowerPC routines such as `bzero.S` / `memset` to choose cache-block operations. Failure to retrieve sysctl data is tolerated; consumers must handle zero/unknown cache info.
