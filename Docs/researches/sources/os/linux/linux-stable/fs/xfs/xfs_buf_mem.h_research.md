# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.h

## Purpose
Declares constants and helpers for XFS memory-backed buffer targets.

## Main Contents
Defines `XMBUF_BLOCKSIZE` and `XMBUF_BLOCKSHIFT` as page-size/page-shift. Under `CONFIG_XFS_MEMORY_BUFS`, `xfs_buftarg_is_mem` identifies memory targets by `bt_bdev == NULL` and declares allocation, free, address verification, transaction detach, and finalize helpers.

## Configuration Behavior
Without `CONFIG_XFS_MEMORY_BUFS`, memory-buffer detection and address verification are compile-time false. `xmbuf_map_backing_mem` remains declared outside the feature guard for buffer-cache integration.
