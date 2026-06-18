# File Research: sources/os/linux/linux/fs/xfs/xfs_fsmap.h

Defines internal fsmap data structures and ioctl entry point.

Key contents:
- `struct xfs_fsmap`: internal mapping record with device, flags, physical offset, owner, owner offset, and length in filesystem units.
- `struct xfs_fsmap_head`: internal request/response header with flags, counts, and low/high keys.
- `struct xfs_fsmap_irec`: normalized internal record derived from rmap/free-space metadata, including start daddr, length, owner, offset, rmap flags, and original rmap startblock key.
- Declares `xfs_ioc_getfsmap`.

This header isolates the byte-to-basic-block conversion and internal record shape used by fsmap query backends.
