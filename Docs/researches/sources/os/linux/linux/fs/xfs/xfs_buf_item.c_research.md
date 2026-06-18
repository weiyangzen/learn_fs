# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item.c

Implements the in-core buffer log item lifecycle for XFS metadata buffers. It allocates and frees `struct xfs_buf_log_item`, tracks dirty bitmap ranges per buffer segment, formats dirty ranges into log vectors, pins/unpins buffers during log commit, pushes dirty buffers from the AIL, and releases or invalidates stale buffers.

Key behavior:
- `xfs_buf_item_init` attaches a log item to a buffer and creates one log-format bitmap per buffer map segment.
- `xfs_buf_item_log` marks byte ranges dirty in `XFS_BLF_CHUNK` units, handling discontiguous buffers segment by segment.
- `xfs_buf_item_size` and `xfs_buf_item_format` compute and emit log vectors, including stale/cancel and ordered-buffer special cases.
- Pin/unpin logic deliberately holds buffer and BLI references to avoid races with AIL I/O completion and shutdown abort paths.
- Stale buffers use `XFS_BLF_CANCEL`; stale inode buffers also trigger inode-specific I/O completion.
- `xfs_buf_item_done` removes a buffer log item from the AIL and releases it after writeback or recovery write completion.

This file is central to XFS physical metadata logging. Correctness depends on reference counts, buffer locks, AIL membership, and dirty bitmap consistency.
