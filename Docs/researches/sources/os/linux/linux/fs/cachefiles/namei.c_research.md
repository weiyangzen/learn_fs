# File Research: sources/os/linux/linux/fs/cachefiles/namei.c

## Purpose
Handles CacheFiles backing filesystem namespace operations: directory creation/pinning, inode in-use marking, file lookup/open/create, tmpfile commit, unlink/rename-to-graveyard deletion, daemon culling, and in-use checks.

## Main Elements
- In-use marking: `__cachefiles_mark_inode_in_use()`, `cachefiles_mark_inode_in_use()`, `__cachefiles_unmark_inode_in_use()`, and `cachefiles_unmark_inode_in_use()` use `S_KERNEL_FILE` to prevent culling/removal of active cache entries.
- Directory management: `cachefiles_get_directory()` looks up or creates cache directories, validates required inode operations, and pins them; `cachefiles_put_directory()` unmarks and releases them.
- Removal helpers: `cachefiles_unlink()`, `cachefiles_bury_object()`, and `cachefiles_delete_object()` unlink files or rename directories into the graveyard.
- Tmpfile handling: `cachefiles_create_tmpfile()` creates an unlinked direct-I/O backing file, marks it in use, initializes on-demand state, sizes it, and validates read/write iter ops.
- Object creation/open: `cachefiles_create_file()`, `cachefiles_open_file()`, and `cachefiles_look_up_object()` locate existing cache files, validate xattrs, replace stale files, or create tmpfiles.
- Tmpfile commit: `cachefiles_commit_tmpfile()` links an unlinked tmpfile into the fanout directory, replacing stale objects if needed.
- Daemon operations: `cachefiles_lookup_for_cull()`, `cachefiles_cull()`, and `cachefiles_check_in_use()`.

## Dependencies And Integration
Works under CacheFiles security overrides from callers. Integrates VFS helpers for create/remove/rename/link/tmpfile/open, LSM path checks, xattr coherency, on-demand initialization, CacheFiles volume fanout directories, and daemon culling commands.

## Risk Notes
Namespace races are handled through VFS `start_creating`, `start_removing`, and rename helpers plus `S_KERNEL_FILE`, but failures can leave objects stale or force cache shutdown on serious I/O/security errors. Directory objects are moved to a graveyard instead of directly removed. Active-file detection relies on inode flags shared with culling.
