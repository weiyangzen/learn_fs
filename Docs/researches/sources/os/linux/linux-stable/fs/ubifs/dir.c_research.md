# File Research: sources/os/linux/linux-stable/fs/ubifs/dir.c

UBIFS directory and namespace operations: inode creation, lookup, readdir, link/unlink, mkdir/rmdir, mknod, symlink, rename, tmpfile, getattr, and directory file operations.

Key responsibilities:
- Implements VFS directory inode operations table `ubifs_dir_inode_operations`.
- Implements directory file operations table `ubifs_dir_operations`.
- Creates UBIFS inodes with journaling/recovery-safe orphan handling in `ubifs_new_inode()`.
- Handles fscrypt-aware filename setup, lookup, readdir, links, symlinks, and renames.
- Maintains directory `i_size`, `ui_size`, link counts, timestamps, budgets, and journal updates atomically around namespace changes.

Important behavior:
- New non-xattr inodes are created with zero link count and placed on the orphan list until the journal update links them into the namespace. This protects against power cuts between security/encryption xattr setup and dentry creation.
- Most operations budget space before writing and then immediately journal changed inodes instead of simply marking them dirty. Unlink/rmdir may continue after `-ENOSPC` because UBIFS reserves deletion space.
- `ubifs_lookup()` supports encrypted no-key names via hash/minor hash lookup and validates encryption context consistency for encrypted directories.
- `ubifs_readdir()` maps UBIFS key hashes to directory offsets, saves the current dent in `file->private_data`, and explicitly notes that UBIFS cannot provide full NFS-style seekdir/telldir semantics due to hash collisions.
- `ubifs_check_dir_empty()` scans for the first dentry and returns `0`, `-ENOTEMPTY`, or lookup error.
- `do_rename()` supports overwrite and `RENAME_WHITEOUT`; `ubifs_xrename()` supports `RENAME_EXCHANGE`.
- `ubifs_getattr()` reports UBIFS flags through statx attributes and returns zero block count for non-regular files to avoid misleading block-device-style accounting.

Locking and budgeting:
- `ui_mutex` protects UBIFS inode-private size/dirty state during journal updates.
- `lock_2_inodes()` and `lock_4_inodes()` rely on VFS inode lock ordering and use nested lock classes.
- Rename budgets separate the namespace update request, old inode dirtying request, and optional whiteout inode request to avoid deadlocks with writeback.

Cross-file links:
- Calls `ubifs_jnl_update()`, `ubifs_jnl_rename()`, and `ubifs_jnl_xrename()` to persist namespace changes.
- Uses fscrypt operations from `crypto.c`.
- Uses debug checks from `debug.c`/`debug.h`, especially synced inode size and directory accounting checks.
- Regular files created here use address-space and file operations from `file.c`.

Invariants and risks:
- Directory `i_size` is logical UBIFS dentry accounting, not byte stream content.
- Deletion paths intentionally clear no-space flags after unbudgeted delete progress.
- Error paths carefully restore link counts and directory sizes; these paths are critical because journal update failure occurs after in-memory mutation.
