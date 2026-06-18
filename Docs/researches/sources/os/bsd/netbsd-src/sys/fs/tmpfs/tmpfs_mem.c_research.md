# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_mem.c

Read completely: 238 lines.

This implements tmpfs memory accounting and allocation helpers. Per-mount accounting is initialized, destroyed, and resized through `tm_acc_lock`. Available memory is computed from swap, available memory, file pages, wired pages, and `uvmexp.freetarg`; effective maximum bytes are the smaller of the configured mount limit and currently available system capacity.

The file accounts node structures, dirent structures, regular-file pages, and rounded name allocations against `tm_bytes_used`. It also enforces `tm_nodes_max` with atomic node counters and provides pool-backed allocation/free wrappers for nodes and dirents.

Important interactions: `tmpfs_subr.c` uses these helpers for node, dirent, symlink/name, and regular-file page accounting. `tmpfs_vfsops.c` uses them for mount limits and statvfs.

Security/reliability notes: `tmpfs_mem_incr` rejects allocations when `used + sz >= limit`, leaving one-byte/page headroom by comparison style. Name allocations are rounded to 32-byte quanta and asserted to be no larger than 1024 bytes.
