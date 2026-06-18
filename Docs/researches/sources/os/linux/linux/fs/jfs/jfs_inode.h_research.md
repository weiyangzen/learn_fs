# File Research: sources/os/linux/linux/fs/jfs/jfs_inode.h

## Role

Declares JFS inode, file, directory, export, ioctl, block-mapping, writeback, truncate, xattr/attribute, and operation-table interfaces.

## Key Responsibilities

- Declares inode allocation and lookup helpers: `ialloc()` and `jfs_iget()`.
- Declares sync/writeback/dirty/evict/commit paths.
- Declares truncate and zero-link free helpers.
- Declares exportfs helpers for parent and file-handle resolution.
- Declares inode flag and block mapping helpers.
- Declares setattr and file-attribute get/set interfaces.
- Declares ioctl entry point.
- Exposes operation tables for address-space operations, directory/file/symlink inode operations, directory/file file operations, fast symlink operations, and case-insensitive dentry operations.

## Important Interactions

- Implemented across multiple JFS source files, including `jfs_inode.c`, generic inode/file/dir/namei/ioctl code, and export helpers.
- Included by allocation, extent, and imap code when they need inode lifecycle or commit entry points.

## Invariants and Risks

- This header is a cross-module contract; prototype drift would break many JFS compilation units.
- `jfs_fileattr_set()` uses modern idmapped mount parameters via `struct mnt_idmap`.
- `jfs_get_block()` is the bridge from VFS/buffer-head mapping to JFS extent logic.
