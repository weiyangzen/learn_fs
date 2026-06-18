# sources/storage-engines/wiredtiger/src/cursor/cur_backup_incr.c

## Purpose
This file implements duplicate backup cursors for block-based incremental backup. Given a file selected by the primary backup cursor, it returns either whole-file copy ranges or modified block ranges derived from checkpoint backup metadata.

## Important APIs, Types, and Functions
Public functions are `__wt_backup_load_incr`, `__wti_curbackup_free_incr`, and `__wti_curbackup_open_incr`. Local helpers are `__curbackup_incr_blkmod` and `__curbackup_incr_next`. Important state is held in `WT_CURSOR_BACKUP`: `incr_src`, `incr_file`, `incr_cursor`, `cfg_current`, `bitstring`, `granularity`, `nbits`, `offset`, `bit_offset`, and flags such as `WT_CURBACKUP_INCR_INIT`, `WT_CURBACKUP_FORCE_FULL`, `WT_CURBACKUP_RENAME`, `WT_CURBACKUP_CKPT_FAKE`, `WT_CURBACKUP_HAS_CB_INFO`, `WT_CURBACKUP_COMPRESSED`, and `WT_CURBACKUP_CONSOLIDATE`.

## Control Flow and Behavior
`__wti_curbackup_open_incr` converts a duplicate backup cursor into an incremental range cursor by replacing its `next` method, inheriting the source incremental ID and current metadata config from the primary cursor, forcing full copies for WiredTiger-owned files or source IDs marked full, inheriting consolidation mode, and opening a file cursor on the target file when range metadata can be used.

`__curbackup_incr_next` returns one key per full file or modified range. If no btree cursor exists or the file is force-full/rename, it returns a `WT_BACKUP_FILE` key with offset 0 and file size, then reports `WT_NOTFOUND` on the next call. Otherwise it lazily loads checkpoint backup info via `__curbackup_incr_blkmod`, which parses `checkpoint_backup_info` for the source ID, detects compression, fake checkpoints, rename markers, granularity, bit count, base offset, and hex-encoded modified-block bitstrings. Iteration scans the bitstring for set bits and returns `WT_BACKUP_RANGE` keys; consolidation merges contiguous set bits into one returned range while still counting every block in stats.

## State and Persistence
Persistent inputs are per-file metadata fields, especially `checkpoint_backup_info` and block modification bitstrings. Cursor state is volatile and advances through `bit_offset`. Full-copy fallback uses filesystem size. The code does not write metadata; it interprets metadata produced by checkpoint/backup machinery.

## Dependencies and Integration Points
The file depends on the main backup cursor, metadata checkpoint parsing, config parsing, file cursor opening, filesystem size calls, log filename handling, statistics, btree dhandles, and cursor API macros.

## Risks
Risks include corrupted bitstrings, mismatch between `nbits` and decoded bytes, stale `cfg_current`, incorrect full-copy fallback for renamed/new files, cursor-cache interaction when opening internal file cursors, and accidentally returning compressed/uncompressed stats under the wrong dhandle.

## Test Signals
Signals include full-file keys for WiredTiger/log/renamed/new fake-checkpoint files, range keys for modified blocks, consolidated contiguous ranges, `WT_NOTFOUND` for unchanged files, corrupted modified block list errors, and correct backup block statistics.
