# File Research: sources/os/linux/linux-stable/fs/ubifs/xattr.c

## Summary
Implements UBIFS extended attributes. UBIFS stores each xattr value as a special regular inode with inline data and stores each xattr name as an xentry, reusing directory-entry and TNC mechanisms.

## Key Functions
- `ubifs_xattr_set()`: creates or replaces xattrs, enforcing size, name length, and `XATTR_CREATE` / `XATTR_REPLACE`.
- `ubifs_xattr_get()`: looks up the xentry, loads the xattr inode, and returns or copies the inline value.
- `ubifs_listxattr()`: iterates xentries and emits visible xattr names.
- `ubifs_purge_xattrs()`: non-atomically removes xattrs when an inode exceeds current xattr-count limits.
- `ubifs_xattr_remove()`: removes one xattr by name.
- `ubifs_init_security()`: initializes security xattrs through LSM support when enabled.
- `create_xattr()`, `change_xattr()`, `remove_xattr()`: internal helpers that handle budgeting, inode/xentry journaling, ctime updates, and host xattr accounting.

## Important Behavior
Xattr values are limited to `UBIFS_MAX_INO_DATA` because they are stored as inode-attached data. Xattr inodes are synchronous, noatime/nocmtime, have empty inode/file operations, and are not compressed.

Host inode accounting tracks xattr count, total on-flash xattr size, and total xattr name bytes. `create_xattr()` also enforces `XATTR_LIST_MAX` by considering names plus null terminators.

The internal encryption-context xattr named `c` is hidden from list output and also sets `UBIFS_CRYPT_FL` on the host inode during creation.

`xattr_sem` serializes xattr create/replace/remove/list/get operations per host inode. `ui_mutex` protects host inode accounting updates and ctime changes while journal updates are prepared.

## Risks
Xattrs are modeled as normal inodes, so journal ordering matters. `change_xattr()` deliberately writes the xattr inode before the host inode so host `fsync()` also synchronizes the value. Error paths roll back host accounting and may mark damaged xattr inodes bad; missing rollback would permanently skew xattr size/count accounting.
