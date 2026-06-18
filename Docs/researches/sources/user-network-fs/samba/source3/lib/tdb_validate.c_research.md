## sources/user-network-fs/samba/source3/lib/tdb_validate.c

Purpose: validation and backup/repair helper for Samba TDB databases. It verifies TDB structural integrity and caller-specific records, creates rotating backups for valid databases, and attempts restore from backup when corruption is detected.

Important functions are `tdb_validate`, `tdb_validate_open`, `tdb_validate_and_backup`, and private helpers `tdb_validate_child`, `tdb_copy`, `tdb_backup`, `tdb_backup_with_rotate`, and `rename_file_with_suffix`. The status struct tracks `tdb_error`, `bad_freelist`, `bad_entry`, `unknown_key`, and `success`.

Control flow: `tdb_validate` forks a child so validation crashes/panics do not kill the parent. The child runs `tdb_check`, validates freelist, traverses records with the caller callback, and exits with status. The parent waits and maps exit/signal/stop to a nonzero result. Backup opens and locks the source TDB, copies all records into `dst.tmp`, verifies traversal count, fsyncs, and atomically renames. `tdb_validate_and_backup` backs up valid DBs to `.bak` with `.old` rotation; for invalid DBs it checks `.bak`, moves corrupt originals to `.corrupt`, and restores the backup, with ENOSPC fallback options.

State and persistence: it mutates filesystem state by creating `.bak`, `.old`, `.tmp`, and `.corrupt` files and renaming/restoring databases. Dependencies are TDB APIs, Samba `util_tdb`, fork/wait, stat/rename/unlink/fsync, talloc, and debug.

Risks: forked validation inherits process state; open locks and callbacks must be fork-safe. Backup success is ignored after a valid validation, intentionally returning success even if backup creation fails. ENOSPC fallback may rename the source as last resort during restore. Tests should cover child signal handling, corrupt freelist/record callback statuses, backup rotation, ENOSPC retry paths, and restore from valid/invalid backups.
