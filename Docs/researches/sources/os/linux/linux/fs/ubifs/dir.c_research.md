# File Research: sources/os/linux/linux/fs/ubifs/dir.c

Read completely: 1772 lines.

This file implements UBIFS directory and namespace VFS operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, tmpfile, rename/exchange/whiteout, getattr for directories/files, and directory file operations.

Main entry points: `ubifs_new_inode`, `ubifs_check_dir_empty`, `ubifs_getattr`, `ubifs_dir_inode_operations`, and `ubifs_dir_operations`.

Key behavior: all mutating operations budget space before journaling, except deletion paths (`unlink`, `rmdir`, zero-size-like deletion cases) can continue on `-ENOSPC` using reserved deletion space. Newly created non-xattr inodes start with zero links and are placed on the orphan list until the journal update links them, which protects power-cut consistency around security/encryption xattrs and dentries.

Filesystem semantics covered:
- `lookup` handles fscrypt nokey names, hash/minor-hash lookups, dead-dentry detection, and encrypted context compatibility checks.
- `readdir` maps UBIFS dentry hash keys to VFS offsets and saves the last full dentry in `file->private_data` to handle collisions across consecutive calls.
- create/mkdir/mknod/symlink/tmpfile initialize security, encryption context, inherited flags, data payloads, link counts, parent sizes, and journal updates.
- unlink/rmdir purge xattrs, update link counts and parent sizes, and clear no-space flags when deletion succeeded without a budget.
- rename supports `RENAME_NOREPLACE`, `RENAME_WHITEOUT`, and `RENAME_EXCHANGE`, with multi-inode locking, parent link-count repair, whiteout inode creation, and atomic journal rename records.

Important interactions: uses fscrypt name setup/preparation extensively, calls journal update helpers for atomic media changes, uses UBIFS inode `ui_mutex` for internal size/link updates, and relies on `file.c` for `ubifs_fsync`, `ubifs_setattr`, and file operations assigned to regular inodes.

Reliability notes: directory offsets are hash-based, so full `seekdir`/`telldir` semantics are not guaranteed and NFS is explicitly unsuitable. Error unwind paths restore parent sizes, link counts, budgets, inode refs, and fscrypt names carefully; rename/whiteout remains the most stateful path.
