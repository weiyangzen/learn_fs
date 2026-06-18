# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log_recover.c

## Purpose
Implements XFS journal recovery: log head/tail discovery, log record validation, two-pass item replay, deferred intent recovery, stale block clearing, unlinked inode cleanup, and post-recovery CoW staging cleanup.

## Main APIs
- `xlog_recover` locates the active log range, validates superblock LSN/log features, and starts first-stage recovery.
- `xlog_recover_finish` completes recovered intents, processes AGI unlinked inode lists, and frees leftover CoW staging extents.
- `xlog_recover_cancel` cancels pending recovered intents after mount failure.
- `xlog_recover_iget` and `xlog_recover_iget_handle` acquire inodes for intent recovery, with generation validation for newer file-handle-like intents.
- `xlog_recover_intent_item`, `xlog_recover_release_intent`, and `xlog_recover_finish_intent` manage recovered intent/done item lifecycle.
- `xlog_buf_readahead` issues metadata readahead unless the target buffer is canceled.

## Log Discovery
The file reads the physical circular log in sector-aligned units, verifies block ranges, and handles non-sector-aligned logical offsets inside sector-sized buffers. It finds the head by scanning cycle numbers, detecting zeroed logs, backing up over partial records, and checking log record headers. Tail discovery uses the last good record’s tail LSN, detects clean unmount records, sets in-core log state, and clears stale blocks ahead of the head when the device is writable.

## CRC and Torn Write Handling
Recovery performs CRC verification over candidate head records and treats bad CRCs within the possible in-flight iclog window as torn writes, truncating the head to the first bad record and revalidating the tail. Tail validation can advance past overwritten records close to the head, but returns corruption when bad records are outside the safe overwrite window.

## Replay Pipeline
Recovery uses registered per-item operations for buffer, inode, dquot, quotaoff, icreate, extent-free, reverse-map, refcount, bmap, attr, exchange-range, and realtime intent/done items. Pass 1 records canceled buffer items; pass 2 replays live items. Transactions are rebuilt from operation headers, including split/continued regions, then reordered so ordinary buffers precede non-buffer items, inode-unlink buffers replay late, and cancel records replay last.

## Ordering and Writeback
Recovered dirty buffers are submitted only when the recovery LSN changes, preventing metadata LSN updates from causing same-LSN log items to be skipped. On item recovery error, the filesystem is shut down before delayed-write submission so partial checkpoint writeback cannot compromise future recovery.

## Finish Phase
After first-stage item replay, recovery finishes pending log intents through normal deferred-operation transactions, forces the log, rebuilds and drains AGI unlinked inode lists, clears unrecoverable AGI buckets when needed, and frees all leftover reflink CoW staging extents.

## Failure Handling
Malformed headers, bad operation lengths, unknown item types, invalid region counts, incompatible UUID/format, read-only devices needing recovery, unknown incompatible log features, bad CRCs, and metadata corruption return fatal errors. Intent failures force log I/O shutdown and cancel unprocessed intent items.
