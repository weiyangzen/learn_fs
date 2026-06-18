# File Research: sources/os/linux/linux/fs/fat/misc.c

## Purpose
Shared FAT utility implementation for error handling, FSINFO flushing, chain append, timestamp conversion/truncation, inode time updates, and buffer-head syncing.

## Main Responsibilities
- Implements FAT error policy: continue, panic, or remount read-only.
- Prints FAT-prefixed kernel messages.
- Flushes FAT32 free-cluster/next-cluster FSINFO fields.
- Appends newly allocated clusters to inode chains.
- Converts between FAT date/time fields and Unix `timespec64`.
- Applies FAT timestamp granularity rules.
- Syncs arrays of dirty buffer heads.

## Key Interfaces
- `__fat_fs_error()`: central filesystem corruption/error handler.
- `_fat_msg()`: FAT message printer used by `fat_msg()`.
- `fat_clusters_flush()`: writes FAT32 FSINFO free cluster hints.
- `fat_chain_add()`: links new clusters to an inode chain and updates block count.
- `fat_time_fat2unix()` / `fat_time_unix2fat()`: FAT/Unix timestamp conversion.
- `fat_truncate_atime()`: truncates atime to local midnight.
- `fat_truncate_time()` / `fat_update_time()`: applies FAT time granularity to inodes.
- `fat_sync_bhs()`: writes and waits for buffer-head arrays.

## Important Behavior
`__fat_fs_error()` only logs if the caller requested reporting, then follows the mount `errors=` policy. The default remount-read-only path sets `SB_RDONLY` and logs the transition.

`fat_chain_add()` locates the current EOF, writes the previous last cluster to point at the new cluster, or sets `i_start/i_logstart` for an empty file. It checks expected file-cluster count against `i_blocks`, invalidating the FAT cluster cache on mismatch.

Timestamp conversion honors either explicit `time_offset`/`tz=UTC` mount options or the kernel timezone fallback. FAT dates are clamped to 1980-01-01 through 2107-12-31. mtime/ctime are truncated to 2-second granularity, while atime is truncated to day granularity.

## Dependencies
Uses FAT entry read/write, inode sync, cache invalidation, and metadata state from `fat.h`.

## Research Notes
This file encodes much of FAT’s externally visible compatibility behavior, especially timestamps. KUnit coverage in `fat_test.c` targets these timestamp helpers.
