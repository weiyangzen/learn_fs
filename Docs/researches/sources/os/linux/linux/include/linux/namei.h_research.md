# File Research: sources/os/linux/linux/include/linux/namei.h

## Purpose
Declares Linux pathname lookup/pathwalk interfaces, lookup flags, and helper wrappers for create/remove/rename operations.

## Main Contents
- Symlink recursion limits: `MAX_NESTED_LINKS`, `MAXSYMLINKS`.
- Pathwalk flags:
  - Basic lookup behavior: `LOOKUP_FOLLOW`, `LOOKUP_DIRECTORY`, `LOOKUP_AUTOMOUNT`, `LOOKUP_EMPTY`, `LOOKUP_MOUNTPOINT`, `LOOKUP_RCU`, `LOOKUP_CACHED`, `LOOKUP_PARENT`.
  - Final-component intent flags: `LOOKUP_OPEN`, `LOOKUP_CREATE`, `LOOKUP_EXCL`, `LOOKUP_RENAME_TARGET`.
  - Scoped lookup restrictions: `LOOKUP_NO_SYMLINKS`, `LOOKUP_NO_MAGICLINKS`, `LOOKUP_NO_XDEV`, `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_IS_SCOPED`.
- Path lookup APIs: `user_path_at()`, `kern_path()`, `kern_path_parent()`, `vfs_path_lookup()`, `vfs_path_parent_lookup()`.
- Single-component lookup helpers: `lookup_one()`, unlocked/positive variants, and permission-skipping variants.
- Directory operation lifetime helpers: `start_creating*()`, `start_removing*()`, `end_creating()`, `end_creating_keep()`, `end_removing()`, path variants, and rename start/end helpers.
- Mount traversal helpers: `follow_down_one()`, `follow_down()`, `follow_up()`.
- Utility helpers: `mode_strip_umask()`, `nd_jump_link()`, `nd_terminate_link()`, `retry_estale()`.

## Important Design Points
- Lookup flags are split into pathwalk mode, final-component intent, and scoping groups.
- Create/remove helpers centralize locking, lookup, and dentry lifetime handling for VFS operations.
- `mode_strip_umask()` defers umask stripping for POSIX ACL filesystems and honors `SB_I_NOUMASK`.
- `retry_estale()` implements the common “retry once with `LOOKUP_REVAL`” pattern for stale dentries.

## Cross-File Relationships
- Depends on `fs.h` for `struct renamedata`, inode/superblock helpers, `end_dirop()`, and VFS mode/ACL checks.
- Used by io_uring filesystem opcodes in `io_uring/fs.c` through delayed filename and filename-based VFS helpers.
- Lookup flags are consumed by VFS pathwalk/namei implementation outside this header.

## Risks / Review Notes
- Scoped lookup flags are security-sensitive; incorrect combinations can allow path escape, symlink/magic-link traversal, or mount crossing.
- `end_creating_keep()` takes an extra dentry reference before ending the directory operation; callers must manage the returned reference.
- `retry_estale()` only retries if `LOOKUP_REVAL` was not already set.
