# sources/storage-engines/wiredtiger/test/format/backup.c

## Purpose
`backup.c` implements hot backup testing for format runs, including full backups, block incremental backups, restart recovery of incremental backup source IDs, copying of format-specific files, and verification by opening and verifying the backup copy.

## Important APIs, Types, And Functions
The exported worker is `WT_THREAD_RET backup(void *)`. Static helpers include `check_copy`, `copy_blocks`, `copy_format_files`, `restore_backup_info`, `save_backup_info`, and the `ACTIVE_FILES` list utilities. It uses WiredTiger backup cursors (`session->open_cursor("backup:")`), duplicate incremental backup cursors, `WT_BACKUP_RANGE` and `WT_BACKUP_FILE`, `__wt_copy_and_sync`, `wts_open`, `wts_verify`, and `wts_close`.

## Control Flow
The worker opens a session, initializes two alternating active-file lists, optionally restores the previous incremental backup ID/list on reopen, and then sleeps before each backup cycle. Backup work is serialized with named-checkpoint work through `g.backup_lock`. A full backup creates or refreshes `BACKUP`, copies `CONFIG` and `CONFIG.keylen*`, opens a backup cursor, copies each key either as a whole file or via `copy_blocks`, closes the cursor, releases the lock, prunes files no longer active, saves incremental metadata, and verifies the resulting backup in a separate `CHECK.<id>` directory. Incremental mode periodically restarts with a full backup.

## State And Persistence Behavior
The file persists backup content under `g.home/BACKUP`, verification copies under `CHECK.<id>`, and restart metadata in `BACKUP_INFO` using an atomic temporary-file rename. Incremental block copies use raw `open`, `lseek`, `read`, and `write` into the backup directory, while full-file copies rely on WiredTiger/test utility copy helpers. Active file lists represent backup membership so removed source files are unlinked from the backup.

## Dependencies And Integration Points
It integrates with configuration values `backup`, `backup.incremental`, `backup.incr_granularity`, and `backup.live_restore`; with checkpoint through `g.backup_lock`; with format config persistence through copied `CONFIG` files; and with verification via `wts_prepare_discover` and `wts_verify`. It also uses global `g.backup_id` and `g.backup_incr`, which are set by config parsing.

## Risks And Test Signals
Risks include stale incremental IDs after uncheckpointed metadata, partial system-call copies, active-file pruning mistakes, and backup/checkpoint metadata races. Expected test signals include trace messages for backup cursor open/copy/verify, tolerated `EBUSY` on backup cursor open, `ENOENT` causing incremental restart skip, and fatal verification failures if a backup cannot be reopened or verified.
