# File Research: sources/os/linux/linux-stable/fs/fat/misc.c

This file provides shared FAT helpers for error handling, logging, FSINFO flushing, cluster-chain extension, timestamp conversion, timestamp truncation, and buffer synchronization.

Key responsibilities:
- Apply mount-option-driven behavior for filesystem errors.
- Print FAT-prefixed kernel messages.
- Flush FAT32 FSINFO free-cluster and next-cluster hints.
- Append clusters to an inode chain.
- Convert FAT date/time fields to and from Unix `timespec64`.
- Apply FAT timestamp granularity rules.
- Synchronously write buffer_head arrays.

Important functions:
- `__fat_fs_error()` reports corruption-like filesystem errors and either continues, panics, or remounts read-only based on `errors=`.
- `_fat_msg()` emits FAT-prefixed printk messages.
- `fat_clusters_flush()` writes `free_clusters` and `prev_free` to the FAT32 FSINFO sector when valid.
- `fat_chain_add()` appends a newly allocated cluster chain to an inode, updates start cluster for empty files, validates expected block count, and updates `i_blocks`.
- `fat_time_fat2unix()` converts FAT date/time/centiseconds into Unix time with timezone offset handling.
- `fat_time_unix2fat()` converts Unix time into FAT fields, clamping outside the supported 1980-2107 range.
- `fat_truncate_atime()` truncates access time to local-day granularity.
- `fat_truncate_time()` applies FAT atime and ctime/mtime granularity; root inode timestamps remain zero.
- `fat_update_time()` is the VFS update-time hook.
- `fat_sync_bhs()` writes and waits for a list of dirty buffers.

State and integration:
- Timestamp conversion honors `tz_set` and `time_offset`, otherwise uses system timezone minutes west.
- `fat_chain_add()` relies on `fat_get_cluster()`, `fat_ent_read()`, and `fat_ent_write()` from the cache/FAT-entry layers.
- FSINFO flushing is triggered through the synthetic FSINFO inode write path.

Failure behavior:
- Invalid FSINFO signatures are logged but do not hard-fail flushing.
- Cluster count mismatch during append reports a filesystem error and invalidates the inode cluster cache.
- Buffer sync returns `-EIO` if any written buffer is not uptodate.

Research relevance:
- This is the shared utility layer where FAT’s unusual error policy, timezone-dependent timestamps, and append-chain bookkeeping are centralized.
