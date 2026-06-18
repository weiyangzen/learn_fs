# sources/sync-backup/rsync/delete.c

## Purpose
Provides receiver-side delete helpers for removing files/directories, enforcing max-delete limits, honoring filters/perishable rules, optionally making backups, and tracking delete statistics.

## Important APIs, Types, and Functions
`delete_item(char *fbuf, uint16 mode, uint16 flags)` deletes one path, recursively for directories when requested. `delete_dir_contents()` scans and optionally removes directory contents using `get_dirlist()`, local filters, and recursive calls. `get_del_for_flag()` maps file modes to `DEL_FOR_*` flags. Globals include `ignore_perishable`, `non_perishable_cnt`, and `skipped_deletes`.

## Control Flow
For directories, `delete_item()` first calls `delete_dir_contents()` unless the caller already asserts emptiness. `delete_dir_contents()` pushes local filters, gets a directory file list, detects non-perishable protected entries, optionally recurses, adjusts write permission for owned non-writable entries, and calls `delete_item()` for children. Actual deletion uses `do_rmdir_at()` for directories, `make_backup()` or `robust_unlink()` for files, updates `stats`, and reports failures or max-delete limits.

## State and Persistence Behavior
Mutates filesystem contents, backup destinations, file permissions for deletion, `stats.deleted_*`, `skipped_deletes`, and temporary filter state. It respects `max_delete`, `make_backups`, `backup_dir`, and `backup_suffix`.

## Dependencies and Integration Points
Depends on file-list generation, local filter stack from `exclude.c`, syscall wrappers, backup code, logging, and global stats. Used by generator/receiver code when delete modes or make-room operations require removing destination paths.

## Risks and Test Signals
Risks include deleting protected files when filters are wrong, unsafe permission changes, mount-point handling, recursive path buffer overflow assumptions, backup suffix false positives, and max-delete behavior in make-room mode. Test signals include recursive delete with per-dir filters, `--max-delete`, `--backup`, mount-point preservation, non-writable owned files, vanished files, and all `DEL_FOR_*` make-room error messages.
