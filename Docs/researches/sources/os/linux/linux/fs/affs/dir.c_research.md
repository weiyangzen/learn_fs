# File Research: sources/os/linux/linux/fs/affs/dir.c

Purpose: implements AFFS directory file operations, directory inode operations, and `readdir`.

Key interfaces:
- `affs_dir_operations`: open, llseek with cookie support, iterate, fsync, release, lease.
- `affs_dir_inode_operations`: create, lookup, link, unlink, symlink, mkdir, rmdir, rename, setattr.
- `affs_readdir()`: emits `.`/`..`, walks AFFS hash table buckets and per-bucket hash chains.

Implementation notes:
- Per-open state is `struct affs_dir_data`, storing the last inode and an i_version cookie for faster resumed iteration.
- `ctx->pos` encodes hash bucket in high bits and chain offset in low 16 bits, with positions `0` and `1` reserved for dots.
- Directory iteration locks the directory, reads the directory header block, follows `AFFS_TAIL(...)->hash_chain`, and emits names from AFFS tail records.
- If the inode i_version matches the saved cookie, iteration can jump directly to the saved chain inode.
- Handles extremely long chains by warning when the chain position reaches `0xffff`.

Dependencies:
- Relies on AFFS buffer helpers, directory locking, i_version helpers, and name storage in AFFS header/tail blocks.
- `affs_file_fsync()` is shared with regular files.

Edge cases:
- Unreadable directory/header blocks return `-EIO` or stop iteration.
- `dir_emit()` short-circuit leaves state suitable for a later resumed call.
