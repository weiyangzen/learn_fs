# File Research: sources/os/linux/linux/fs/ubifs/xattr.c

## Purpose
Implements UBIFS extended attribute support. UBIFS stores each xattr value as a synchronous regular inode with attached data, and stores xattr names as xentry nodes similar to directory entries.

## Main Functions
- `create_xattr()`: budgets space, creates an xattr inode, copies value into inode-attached data, updates host xattr counters and ctime, handles encryption context flag, writes journal update.
- `change_xattr()`: replaces xattr inode data, updates host xattr byte accounting, journals xattr inode before host inode.
- `iget_xattr()`: loads an xattr inode and validates that it is marked as xattr.
- `ubifs_xattr_set()`: VFS-facing set/replace/create dispatcher with name/size checks and xattr semaphore serialization.
- `ubifs_xattr_get()`: locates xentry, loads xattr inode, copies or sizes value.
- `ubifs_listxattr()`: iterates xentries through TNC, filters internal encryption context and trusted namespace visibility.
- `remove_xattr()`, `ubifs_xattr_remove()`: remove xentry/xattr inode, update host accounting, nlink handling.
- `ubifs_purge_xattrs()`: non-atomic cleanup path for corrupt/over-limit xattr counts.
- Security-xattr initialization helpers under `CONFIG_UBIFS_FS_SECURITY`.
- Xattr handlers for `user.`, `trusted.`, and optionally `security.` prefixes.

## Important Design Points
- Maximum xattr value size is `UBIFS_MAX_INO_DATA` because values are stored as inode-attached data.
- Xattr names are limited by `UBIFS_MAX_NLEN`, and aggregate list size is constrained by `XATTR_LIST_MAX`.
- Xattrs are synchronous and not compressed, by design.
- Host inode accounting tracks `xattr_cnt`, `xattr_size`, and `xattr_names`.
- `xattr_sem` serializes set/remove/create operations and list/get traversal.
- Encryption context xattr (`"c"`) is hidden from list output and sets `UBIFS_CRYPT_FL` on the host inode.

## Cross-File Relationships
- Depends on `ubifs.h` and `ubifs-media.h` constants/macros.
- Uses TNC lookup/iteration (`ubifs_tnc_lookup_nm`, `ubifs_tnc_next_ent`) and journal APIs (`ubifs_jnl_update`, `ubifs_jnl_change_xattr`, `ubifs_jnl_delete_xattr`).
- Uses inode creation from UBIFS directory code via `ubifs_new_inode()`.

## Risks / Review Notes
- `create_xattr()` clears `UBIFS_CRYPT_FL` on error even if the flag pre-existed; this is intentional-looking but worth caution around multi-xattr encryption-context paths.
- `ubifs_purge_xattrs()` is explicitly non-atomic and used after detecting too many xattrs.
- Error paths often mark xattr inode bad after journal/accounting failures, which is appropriate but makes recovery behavior important.
