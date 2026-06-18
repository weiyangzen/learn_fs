# File Research: sources/os/linux/linux-stable/fs/affs/dir.c

This file provides AFFS directory file operations and directory iteration.

Major responsibilities:
- Defines directory `file_operations` with open, release, llseek with cookies, shared iteration, fsync, and leases.
- Defines directory `inode_operations` for create, lookup, link, unlink, symlink, mkdir, rmdir, rename, and setattr.
- Allocates per-open `struct affs_dir_data`, storing the last emitted inode and directory version cookie.
- Implements `affs_readdir()` over AFFS hash table chains.

Directory iteration model:
- AFFS directories store hash buckets in the directory header block.
- `ctx->pos` encodes `hash_pos` in the upper bits and `chain_pos` in the lower 16 bits, offset by two after dot entries.
- If more than 65535 entries are encountered in a chain, the code warns and advances to the next hash bucket.
- On stable inode version, iteration can resume directly from `data->ino`; otherwise it rewalks from the hash bucket and chain position.
- Entries are read from file header blocks, names are taken from `AFFS_TAIL(...)->name`, and emitted with `DT_UNKNOWN`.

Consistency and locking:
- Directory traversal is protected by `affs_lock_dir()`/`affs_unlock_dir()`.
- Inode versioning is used to decide whether cached readdir position state is still valid.
- Buffer heads for the directory and current file header are released on all normal paths.
- Read errors while following chains return `-EIO` where possible and log AFFS errors.
