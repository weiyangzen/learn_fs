# sources/sync-backup/rsync/backup.c

Purpose: implements `--backup` behavior, creating backup names/directories and preserving replaced destination items.

Important APIs/types/functions: public `get_backup_name()` and `make_backup()`; helpers `validate_backup_dir()`, `copy_valid_path()`, and `link_or_rename()`.

Control flow: backup path construction either appends suffix or maps into `backup_dir`, creating and validating intermediate directories. `make_backup()` stats the existing item, tries hard-link or rename, deletes conflicting backup targets and retries, then falls back to copying or recreating devices/specials/symlinks while preserving selected attrs/ACLs/xattrs.

State and persistence: uses global backup configuration buffers and suffix. Persistent effects include created backup directories/files, links, renamed originals, copied files, and metadata updates.

Dependencies/integration: depends on delete logic, file-list construction, symlink safety, ACL/xattr caches, `set_file_attrs`, root/device flags, and backup logging.

Risks: rename is not atomic for backup semantics and hard-linked files require cleanup. Unsafe symlink handling intentionally skips certain backups. Directory validation deletes non-directory blockers.

Test signals: backup tests in rsync suite plus CI with ACL/xattr/root variants cover major paths.
