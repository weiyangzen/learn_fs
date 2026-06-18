# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item_recover.c

## Purpose
Implements recovery for logged buffer items, including cancellation tracking, replay ordering, type validation, LSN-based replay skipping, inode-buffer special replay, dquot-buffer handling, and primary superblock grow recovery.

## Main APIs
- `xlog_buf_item_ops` wires buffer item reorder, readahead, pass1, and pass2 recovery callbacks.
- `xlog_alloc_buf_cancel_table`, `xlog_free_buf_cancel_table`, and debug `xlog_check_buf_cancel_table` manage the cancellation hash table.
- `xlog_is_buffer_cancelled` exposes cancel-table lookup.

## Key Behavior
Recovery pass 1 records `XFS_BLF_CANCEL` buffer items by block/length with a refcount so pass 2 can suppress replay until the final cancel record is consumed. Reordering sends normal buffers first, inode buffers later, and cancel records last.

Pass 2 skips canceled buffers, reads the target block, compares on-disk metadata LSNs for CRC filesystems, and replays only when the log item is newer or the current block cannot be trusted. Skipped buffers still get verifier ops attached and read-verified when possible.

## Specialized Replay
Regular buffer replay copies logged chunk vectors into the destination buffer according to the dirty bitmap. Dquot buffers are suppressed if quotaoff was logged for that quota type. Inode buffers replay only `di_next_unlinked` fields unless they are full newly allocated inode buffers. Primary superblock replay updates in-core superblock, data/realtime buftarg sizes, last AG/rtgroup sizing, perag/rtgroup initialization, and allocator set-aside state.

## Metadata Validation
`xlog_recover_validate_buf_type` maps log buffer type flags and on-disk magic values to the correct buffer verifier ops. `xlog_recover_get_buf_lsn` extracts LSN/UUID pairs from many metadata formats and forces replay for unrecognized, stale, inode, dquot, or non-CRC cases.

## Failure Handling
Malformed vectors, bad dquot records, impossible grow/shrink state, verifier failures, and corrupted inode-buffer unlinked fields return corruption errors. Recovery queues dirty buffers for delayed write with `_XBF_LOGRECOVERY`.
