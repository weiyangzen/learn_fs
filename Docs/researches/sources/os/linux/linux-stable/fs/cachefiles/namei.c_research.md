# File Research: sources/os/linux/linux-stable/fs/cachefiles/namei.c

This file handles CacheFiles backing filesystem path walking, directory creation, object file lookup, tmpfile creation/commit, culling, and deletion.

In-use marking:
- Uses inode flag `S_KERNEL_FILE` to mark cache directories/files as actively used by CacheFiles.
- `cachefiles_mark_inode_in_use()` and unmark helpers serialize with inode lock.
- Culling checks this flag to avoid deleting active cache files.

Directory management:
- `cachefiles_get_directory()` looks up or creates a subdirectory, marks it in use, validates it is searchable, supports required directory operations and xattrs, and returns a pinned dentry.
- `cachefiles_put_directory()` unmarks and drops a directory dentry.

Object deletion and burial:
- `cachefiles_unlink()` performs security check and `vfs_unlink()`, with EIO mapped to cache I/O error.
- `cachefiles_bury_object()` unlinks regular files directly, but renames directories into the graveyard using unique names so userspace can later clean them up.
- It handles stale dentries, mountpoints, rename security checks, collision retry, and graveyard loop prevention.
- `cachefiles_delete_object()` removes a cache file from its fanout directory.

Tmpfile and file creation:
- `cachefiles_create_tmpfile()` opens an unlinked tmpfile in the fanout directory with `O_RDWR | O_LARGEFILE | O_DIRECT`, marks it in use, initializes on-demand state, sizes it to rounded DIO object size, and verifies read/write iter support.
- `cachefiles_create_file()` checks file-space availability, creates a tmpfile, marks the cookie needing update, flags object as using tmpfile, and stores `object->file`.
- `cachefiles_commit_tmpfile()` links a tmpfile into the final fanout/name location, replacing stale existing entries if needed, and clears the tmpfile flag on success.

Existing object lookup:
- `cachefiles_look_up_object()` looks up `cache/volume/fanout/object-name`.
- Missing entries create new tmpfiles.
- Non-regular stale/weird entries are buried, then recreated.
- Regular files are opened by `cachefiles_open_file()`, which marks in use, opens direct I/O file handle, initializes on-demand state, checks auxdata xattr coherency, clears no-data flag, sets `object->file`, and touches atime.

Culling:
- `cachefiles_lookup_for_cull()` gets a removable dentry and rejects files marked `S_KERNEL_FILE`.
- `cachefiles_cull()` marks the victim as kernel file to prevent reuse, buries it, and counts the cull.
- `cachefiles_check_in_use()` returns whether a named object is busy or available.

Important interactions:
- Fanout directory is selected by low byte of `cookie->key_hash`.
- All backing VFS operations rely on secure credential overrides set by callers.
- Error injection hooks are present around lookup, mkdir, tmpfile, truncate, link, rename, and unlink paths.
