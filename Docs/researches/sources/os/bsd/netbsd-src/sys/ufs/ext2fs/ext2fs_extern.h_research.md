# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extern.h

This is the central ext2fs internal/public kernel prototype header.

Key contents:
- Forward declarations for kernel VFS, vnode, inode, mount, directory, and buffer-related types.
- External pools: `ext2fs_inode_pool`, `ext2fs_dinode_pool`.
- `EXT2FS_ITIMES` macro to apply pending inode time updates.
- Prototypes grouped by implementation file:
  - Allocation: `ext2fs_alloc`, `ext2fs_realloccg`, `ext2fs_valloc`, `ext2fs_blkpref`, `ext2fs_blkfree`, `ext2fs_vfree`, `ext2fs_cg_verify_and_initialize`.
  - Block allocation: `ext2fs_balloc`, `ext2fs_gop_alloc`.
  - Mapping: `ext2fs_bmap`.
  - Inode lifecycle: size/block count helpers, update, truncate, inactive.
  - Lookup/directory operations.
  - Subroutines and time updates.
  - VFS operations.
  - Read/write operations.
  - Vnode operations.
  - HTree hash/index operations.
- `IS_EXT2_VNODE` tag check.
- External vnode operation vectors.

Dependencies:
- Assumes UFS/VFS kernel context where `VFS_PROTOS`, `IN_*` flags, and vnode operation declarations exist.

Design notes:
- This header ties the ext2fs implementation files together and exposes the filesystem’s VFS/VOP surface to the rest of the kernel.
