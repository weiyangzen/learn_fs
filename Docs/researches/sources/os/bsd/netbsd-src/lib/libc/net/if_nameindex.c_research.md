# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_nameindex.c

Implementation of `if_nameindex()` and `if_freenameindex()`. It gathers interfaces with `getifaddrs()`, counts AF_LINK entries and total name storage, then performs one allocation containing the `struct if_nameindex` array plus all copied interface names.

The result is terminated with `{ 0, NULL }`. `if_freenameindex()` frees the single allocation returned by `if_nameindex()`.
