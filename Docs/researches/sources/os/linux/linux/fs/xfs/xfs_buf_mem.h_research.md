# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_mem.h

Declares the memory-backed buffer target interface.

Key contents:
- Defines `XMBUF_BLOCKSIZE` and `XMBUF_BLOCKSHIFT` as PAGE_SIZE/PAGE_SHIFT.
- Under `CONFIG_XFS_MEMORY_BUFS`, `xfs_buftarg_is_mem` identifies buftargs with no block device.
- Declares allocation/free, address verification, transaction detach, finalize, and backing-memory mapping helpers.
- Without memory buffer support, most helpers collapse to simple false/no-op style macros, while `xmbuf_map_backing_mem` remains declared for shared build integration.

This header isolates conditional memory-buffer support from the rest of XFS buffer-cache code.
