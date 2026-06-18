# File Research: sources/os/linux/linux/fs/xfs/xfs_filestream.h

Declares filestream lifecycle and allocation selection APIs.

Key contents:
- Mount/unmount helpers for the filestream MRU cache.
- `xfs_filestream_deassociate` to remove an inode’s association.
- `xfs_filestream_select_ag` for allocator integration.
- `xfs_inode_is_filestream` tests mount-wide filestream mode or per-inode filestream flag.

This header is the allocator-facing interface for AG affinity decisions.
