# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_inode.c

Implements ext2 inode size, lifetime, update, and truncation logic. It is derived from FFS inode code but maps ext2 on-disk fields through `i_e2fs_*`.

Key entry points:
- `ext2fs_size()` combines low and high size fields only for regular files.
- `ext2fs_setsize()` enforces `e2fs_maxfilesize`, updates high size for regular/new inodes, and marks large-file rocompat support when needed.
- `ext2fs_inactive()` truncates and frees zero-link inodes on last reference, sets deletion time, writes metadata, and recycles deleted/stale inodes.
- `ext2fs_update()` writes the in-memory dinode back to its inode-table block, including split 32-bit uid/gid storage.
- `ext2fs_truncate()` handles growth, shrink, page-cache invalidation, block pointer clearing, and block release.
- `ext2fs_indirtrunc()` recursively frees single, double, and triple indirect blocks.

Important behavior:
- Truncation first writes a shortened inode to disk, then frees removed blocks, reducing crash windows where live inode pointers reference freed blocks.
- Fast symlinks are stored in the inode and are zeroed directly when truncated to zero.
- Partial-block truncation zeroes bytes after EOF before freeing later blocks.
- Direct and indirect block accounting decrements `i_e2fs_nblock` using disk-block counts.
- Indirect block reads set `b_blkno` manually because bmap would fail after parent pointers have been removed.

Dependencies:
- Uses UFS vnode/inode scaffolding, buffer cache, `ext2fs_buf_alloc()`, `ext2fs_blkfree()`, and endian helpers.
- Closely parallels `ffs_inode.c`, but ext2 lacks FFS fragment-size handling and quota calls here.

Watch points:
- Triple indirect support is explicitly noted as untested.
- `allerror` is assigned after an earlier possible update error path, so error preservation depends on later flow.
- `ext2fs_setsize()` may mark `EXT2F_ROCOMPAT_LARGE_FILE` but still returns `EFBIG` when the requested size exceeds the computed max.
