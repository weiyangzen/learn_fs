# sources/storage-engines/wiredtiger/test/utility/backup.c

## Purpose

`backup.c` implements test helper routines for full and incremental backups, backup cleanup, backup ID discovery, and simple file copy into backup directories.

## Important APIs, Types, and Functions

Exports include `testutil_backup_create_full`, `testutil_backup_create_incremental`, `testutil_backup_force_stop`, `testutil_backup_force_stop_conn`, `testutil_last_backup_id`, `testutil_delete_old_backups`, `testutil_create_backup_directory`, and `testutil_copy_file`. Internal helper `__int_comparator` supports sorting backup IDs.

## Control Flow

Full backup creates `BACKUP_BASE<id>`, opens a backup cursor with incremental metadata enabled, copies each listed file, closes resources, and writes `full` and `done` sentinels. Incremental backup opens a source/destination incremental cursor, copies full files or changed ranges over a base copy, hard-links unchanged files on Unix, and writes `done`.

## State and Persistence Behavior

It creates, removes, renames, hard-links, and writes backup directories/files. Sentinel files mark full backups and completed backups; incomplete backup directories are removed by cleanup.

## Dependencies and Integration Points

Depends on WiredTiger backup cursors, `WT_BACKUP_FILE`/`WT_BACKUP_RANGE`, POSIX file I/O, `testutil_copy`, `testutil_exists`, `testutil_remove`, and backup naming macros from `test_util.h`.

## Risks and Edge Cases

Incremental range copying allocates a buffer sized to each range, which can be large. File descriptors use `> 0` checks, so descriptor 0 would not be closed, although normal opens here usually return higher descriptors. Cleanup keeps the latest full backup while deleting older excess backups.

## Test Signals

Signals include expected file/range counts, `done` sentinels, force-stop rejecting `backup:query_id`, and retained backup directory consistency.
