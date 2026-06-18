# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vnops.c

This is the LFS/ULFS vnode operation implementation, derived from UFS vnode code but routed through LFS-specific inode state, directory accessors, allocation, truncation, and update paths.

Key responsibilities:
- Implements vnode operations including open, access, setattr, remove, link, whiteout, rmdir, readdir, readlink, print, pathconf, advisory locks, special-device wrappers, FIFO wrappers, vnode initialization, GOP allocation/update helpers, and buffer I/O.
- Enforces append-only, immutable, snapshot, read-only mount, ownership, chmod/chown, and kauth authorization rules.
- Uses `lfs_update`, `lfs_truncate`, `lfs_balloc`, `lfs_bufrd`, and `lfs_bufwr` rather than FFS/UFS generic writeback paths.
- Handles LFS directory format conversion in `ulfs_readdir`, translating on-disk `LFS_DIRHEADER` records into userspace `struct dirent` entries and optional cookies.
- Handles short symlink reads directly from inode block-pointer storage, preserving historical off-by-one compatibility behavior around `um_maxsymlinklen`.
- Integrates optional LFS quota accounting during access checks and ownership changes.

Important implementation notes:
- Directory operation state is still stashed in inode `i_crap` / lookup-result fields, mirroring old UFS patterns.
- `ulfs_chown` temporarily removes quota usage from the old owner, applies new uid/gid, then rolls back on quota failure.
- `ulfs_gop_alloc` updates EOF incrementally because `lfs_balloc` requires current file size to be up to date before each allocation.
- `ulfs_vinit` installs special-device or FIFO vnode ops based on inode mode and initializes device aliases with byte-swapped `rdev` handling.
