# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_indextoname.c

Implementation of `if_indextoname()`. It calls `getifaddrs()`, scans AF_LINK addresses for a matching `sdl_index`, copies the interface name into the caller-provided buffer with `strlcpy()`, and frees the address list.

If no interface matches, it returns `NULL` and sets `errno` to `ENXIO`; `getifaddrs()` failures preserve their own `errno`.
