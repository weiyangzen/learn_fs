# File Research: sources/os/linux/linux-stable/fs/affs/namei.c

This file implements AFFS pathname operations, dentry hashing/comparison, lookup, creation, deletion, symlink creation, link creation, rename, and export operations.

Major responsibilities:
- Provides DOS and international case-folding functions.
- Defines dentry hash and compare operations that enforce AFFS name limits and optional no-truncate behavior.
- Implements AFFS directory hash calculation.
- Finds directory entries by following the appropriate hash bucket chain.
- Implements VFS lookup, create, mkdir, rmdir, unlink, symlink, link, and rename operations.
- Provides NFS export support through inode-number file handles and parent lookup.

Name handling:
- Names are case-insensitive under either ASCII-only DOS rules or AFFS international rules.
- Names longer than `AFFSNAMEMAX` can compare equal by truncation unless `nofilenametruncate` is active.
- `affs_hash_name()` computes the AFFS on-disk hash by folding each character and using the legacy `hash * 13 + ch` formula modulo directory hash size.

Lookup and object creation:
- `affs_lookup()` locks the parent directory, finds the matching header block, stores the real header block in `d_fsdata`, resolves file hard-link blocks to their original inode, and returns `d_splice_alias()`.
- `affs_create()` and `affs_mkdir()` allocate a new inode, set mode/protection, install file or directory operations, and call `affs_add_entry()`.
- `affs_symlink()` stores AFFS-formatted symlink text in the inode header table area, translating absolute Unix paths into AFFS volume-prefixed form and compressing `.`/`..` path components.
- `affs_link()` creates an `ST_LINKFILE` entry pointing to the original file.

Rename behavior:
- Normal rename removes the old header from its old parent hash, changes the stored name, and inserts it into the new parent hash.
- Existing destinations are removed before insertion unless `RENAME_NOREPLACE` prevents it at VFS level.
- `RENAME_EXCHANGE` removes both headers, swaps names/parents by reinserting each into the opposite location, and marks both metadata buffers dirty.
- Directory hash updates are individually locked by parent directory.

Export support:
- `affs_get_parent()` reads the AFFS parent pointer from the child header.
- `affs_nfs_get_inode()` validates block range then calls `affs_iget()`.
- `affs_export_ops` uses generic 32-bit inode file handle encoding.
