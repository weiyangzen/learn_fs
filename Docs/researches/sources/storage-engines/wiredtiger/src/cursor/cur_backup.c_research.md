# sources/storage-engines/wiredtiger/src/cursor/cur_backup.c

## Purpose
This file implements the main backup cursor, including full hot backup, targeted backup, query-id backup cursors, export backup cursors, incremental backup state management, duplicate backup cursors, and backup metadata file generation.

## Important APIs, Types, and Functions
Public functions include `__wt_verbose_dump_backup`, `__wt_backup_set_blkincr`, `__wt_backup_destroy`, `__wt_backup_open`, `__wt_backup_file_remove`, and `__wt_curbackup_open`. Important local functions are `__curbackup_next`, `__curbackup_reset`, `__curbackup_close`, `__backup_free`, `__backup_add_id`, `__backup_find_id`, `__backup_log_append`, `__backup_config`, `__backup_query_setup`, `__backup_start`, `__backup_stop`, `__backup_all`, `__backup_list_uri_append`, and `__backup_list_append`.

Key structures and flags are `WT_CURSOR_BACKUP`, `WT_BLKINCR`, `WT_CONN_INCR_BACKUP`, `WT_CURBACKUP_LOCKER`, `WT_CURBACKUP_DUP`, `WT_CURBACKUP_INCR`, `WT_CURBACKUP_FORCE_STOP`, `WT_CURBACKUP_QUERYID`, `WT_CURBACKUP_EXPORT`, `WT_BLKINCR_VALID`, `WT_BLKINCR_INUSE`, and `WT_BLKINCR_FULL`.

## Control Flow and Behavior
Opening a backup cursor allocates and initializes a `WT_CURSOR_BACKUP`, handles special URIs (`backup:query_id`, `backup:export`), rejects non-export backup under tiered storage, and starts backup under checkpoint and schema locks for top-level cursors. `__backup_start` rejects in-memory mode, serializes hot backups, handles incremental `force_stop` early, sets the hot-backup flag, optionally creates the temporary backup metadata file, parses backup config, builds target/log/full lists, appends standard WiredTiger files, syncs and renames the temp file, and publishes the list under the hot-backup lock.

`__backup_config` handles incremental enable/granularity, consolidate, duplicate incremental file, source ID, new ID, target lists, log targets, and incompatibility rules. Full backups append active log files before metadata object lists to choose a safe checkpoint/log ordering. `__curbackup_next` returns successive file names as keys and advances parallel config entries for incremental backup. Close handles duplicate cursor cleanup, force-stop destruction, forced checkpoints for incremental metadata visibility, backup file removal, export-file removal, and clearing the connection hot-backup state.

## State and Persistence
Persistent backup state lives in metadata `checkpoint_backup_info` and backup files `WiredTiger.backup`, `WiredTiger.backup.tmp`, `WiredTiger.backup.metadata`, and export backup output. Incremental ID/granularity state is restored from the metadata file on open into `conn->incr_backups` and `conn->incr_granularity`. Volatile state includes open backup cursor flags, `conn->backup.start`, `conn->backup.list`, session backup flags, duplicate cursor flags, and per-cursor lists.

## Dependencies and Integration Points
This file depends on checkpoint/schema/hot-backup locks, metadata scans, schema worker, log manager backup file enumeration, filesystem rename/sync/remove, live-restore metadata cleanup, cursor initialization, tiered storage restrictions, and incremental duplicate cursor support in `cur_backup_incr.c`.

## Risks
Risks include inconsistent backup metadata if temp file handling or rename fails, checkpoint deletion racing with backup start/stop, incremental IDs left in-use on error, incompatible log/incremental/target combinations, stale incremental metadata reappearing without forced checkpoint after stop, and assumptions that metadata `file:` entries map one-to-one to physical files.

## Test Signals
Signals include full backup file lists, target backup object expansion, log backup behavior with log removal disabled/enabled, query-id output, incremental ID restore from metadata, force-stop cleanup plus checkpoint, duplicate cursor restrictions, backup temp file cleanup, and tiered-storage export behavior.
