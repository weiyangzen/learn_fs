# File Research: sources/os/linux/linux/fs/hpfs/dir.c

Purpose: Provides HPFS directory VFS operations for readdir, lookup, directory seek, and file operation tables.

Key functions:
- `hpfs_dir_release()` removes tracked readdir position pointers.
- `hpfs_dir_lseek()` validates HPFS synthetic directory positions by walking dnodes.
- `hpfs_readdir()` emits `.`, `..`, then walks HPFS dnode tree entries using encoded positions, translating case as needed.
- `hpfs_lookup()` validates names, finds dirents in the dnode tree, instantiates or fills inodes, handles directory/file distinction, reads EAs when needed, and rejects unsupported HPFS386 ACL/XPERM structures.
- `hpfs_dir_ops` wires directory llseek/read/iterate/release/fsync/ioctl operations.

Dependencies and integration:
- Uses dnode traversal from `dnode.c`, inode initialization from `inode.c`, name validation/translation from `name.c`, and global HPFS locking.
- Directory positions encode dnode sector plus entry index.

Risk notes:
- Readdir depends on tracked position pointers so directory mutations can adjust active iterators.
- Strict check mode performs additional fnode/dnode consistency validation and cycle detection.
