# File Research: sources/os/bsd/freebsd-src/sbin/nfsiod/nfsiod.c

Userland control utility for NFS async I/O daemon counts. It ensures NFS support is present, reads current `vfs.nfs.iodmin`/`iodmax`, and optionally sets the maximum daemon count.

Key behaviors:
- Loads the `nfs` kernel module if `getvfsbyname("nfs")` initially fails.
- Supports `-n num_servers`, clamped to `[1, 20]`.
- With no `-n`, prints current `iodmin` and `iodmax`.
- When lowering below current `iodmin`, updates `iodmin` first, then sets `iodmax`.

Research notes:
- It is a sysctl control shim, not a daemon implementation.
- Uses `atoi`, so malformed numeric input is treated as zero and then clamped to one.
