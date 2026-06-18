# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/poolio.c

Shared open/ioctl/close wrapper for the IPFilter lookup device.

Key behavior:
- Lazily opens `IPLOOKUP_NAME` read-write unless `OPT_DONTOPEN` is set.
- `pool_ioctl()` calls the supplied ioctl function on the cached descriptor.
- Provides `pool_close()` and `pool_fd()`.

Research notes:
- Uses one static descriptor for the process.
