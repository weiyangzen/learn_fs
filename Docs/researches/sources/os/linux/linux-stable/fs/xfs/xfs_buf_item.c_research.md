# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.c

## Purpose
Implements the in-core XFS buffer log item (`xfs_buf_log_item`) lifecycle: allocation, dirty-range bitmap tracking, log vector sizing/formatting, pin/unpin behavior, AIL push, transaction release, and stale/cancel cleanup.

## Main APIs
- `xfs_buf_item_init` attaches a new buffer log item to an `xfs_buf`, allocating one log-format header per buffer map segment.
- `xfs_buf_item_log` marks byte ranges dirty in per-segment bitmaps, using `XFS_BLF_CHUNK` granularity.
- `xfs_buf_item_dirty_format` checks whether any segment bitmap contains logged ranges.
- `xfs_buf_item_put` drops a BLI reference and frees clean non-AIL items.
- `xfs_buf_item_done` removes the buffer log item from the AIL and releases it.
- `xfs_buf_inval_log_space` computes worst-case log format overhead for invalidated/stale buffers.
- `xfs_buf_log_check_iovec` validates recovered buffer log format vector bounds.

## Key Behavior
Buffer log vectors consist of one format record plus one data vector for each contiguous dirty bitmap run. Discontiguous buffers are represented as separate format records, making recovery see them like multiple ordinary buffers. Ordered buffers consume no data vectors; stale buffers log only cancel-format records.

Pinning takes both a BLI ref and a buffer ref so unpin completion cannot race with buffer freeing. Stale completion handles attached inode/dquot completion state, removes AIL state, releases log items, and unlocks/releases the buffer from the final owner path.

## Recovery and Correctness Interactions
The code sets `XFS_BLF_INODE_BUF` at format time for inode buffers, with special handling for newly allocated inode buffers so recovery can distinguish full inode initialization from later unlinked-list-only replay. `xfs_buf_item_committed` preserves the original LSN for newly allocated inode buffers until original inode images are flushed.

## Dependencies
Uses `xfs_bit` bitmap helpers, transaction/log item infrastructure, AIL helpers, buffer cache primitives, quota/dquot and inode buffer completion hooks, tracepoints, and metadata verifiers under `DEBUG_EXPENSIVE`.

## Failure Handling
Oversized dirty bitmap requirements cause `-EFSCORRUPTED` at init. Shutdown/abort paths carefully avoid stale BLI double-free and simulate failed async I/O when an unpin removes an item.
