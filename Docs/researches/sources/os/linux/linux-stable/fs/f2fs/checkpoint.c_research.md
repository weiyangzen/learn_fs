# File Research: sources/os/linux/linux-stable/fs/f2fs/checkpoint.c

## Purpose
Implements F2FS checkpoint coordination, metadata-page IO, block-address validation, dirty/orphan inode tracking, checkpoint pack validation/writing, operation freezing, and asynchronous checkpoint request merging.

## Main Components
- Lock wrappers trace elapsed lock time and can temporarily uplift task priority for selected F2FS rwsems.
- Meta folio helpers read, grab, retry, dirty, write, and readahead metadata pages through `META_MAPPING`.
- Block-address validation checks metadata and data address ranges, SIT bitmap consistency, checkpoint error state, and marks `SBI_NEED_FSCK` on serious inconsistencies.
- Inode-entry management tracks append/update/transition/orphan/flush inode sets with radix trees, lists, and slab cache entries.
- Orphan handling reserves orphan slots, writes orphan blocks into checkpoint packs, and recovers orphan inodes during mount by truncating unlinked files.
- Checkpoint validation reads both checkpoint packs, checks CRC offsets and CRC values, compares versions, and selects the newest valid pack.
- Dirty inode sync flushes dirty directory/file data and inode metadata until checkpoint can proceed.
- `block_operations()` freezes filesystem-changing operations, flushes quota, dentry, inode metadata, and node pages, and prepares checkpoint counts.
- `do_checkpoint()` writes NAT/SIT metadata, checkpoint payload, orphan blocks, summaries, optional NAT bits, checksum, device cache flush, final checkpoint page, and cleanup state.
- `f2fs_write_checkpoint()` coordinates global checkpoint locking, dirty checks, disabled checkpoint handling, NAT/SIT flushes, in-memory current segment save/restore, discard handling, timing stats, and checkpoint error propagation.
- Async checkpoint support queues requests on an llist, services them from `f2fs_ckpt-*` kthread, completes waiters, and tracks latency stats.
- Slab caches are created for inode/orphan tracking entries.

## Important Behaviors
- Checkpoint packs are double-buffered and selected by valid CRC plus newest version.
- The checkpoint writer avoids racing with node updates by holding `cp_rwsem`, `node_change`, and `node_write` in staged order.
- Quota flushing is retried and can set flags requiring later fsck when it cannot be flushed safely.
- Long checkpoint latency is recorded and rate-limited warnings include phase timings.
- Merged checkpoint mode coalesces synchronous checkpoint requests unless disabled by mount/current context.

## Dependencies
Uses F2FS node, segment, iostat, quota, discard, NAT/SIT, summary, writeback, folio, kthread, block-device cache flush, and tracepoint infrastructure.

## Research Notes
This file is central to F2FS crash consistency. Critical invariants include checkpoint pack CRC/version validity, dirty metadata drain ordering, orphan count capacity, NAT/SIT flush completion, and correct lock ordering around operation freeze/unfreeze.
