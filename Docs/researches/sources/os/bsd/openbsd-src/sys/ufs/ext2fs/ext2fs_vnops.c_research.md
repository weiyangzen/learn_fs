# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c

Defines ext2 vnode operations for create, metadata changes, links, rename, directories, symlinks, locking, fsync, reclaim, and vop tables.

Key entry points:
- `ext2fs_create()`, `ext2fs_mknod()`, and `ext2fs_makeinode()` allocate and install new inodes.
- `ext2fs_open()` enforces append-only open semantics.
- `ext2fs_access()`, `ext2fs_getattr()`, and `ext2fs_setattr()` implement permission and attribute operations.
- `ext2fs_chmod()` and `ext2fs_chown()` implement ownership/mode changes.
- `ext2fs_remove()`, `ext2fs_link()`, and `ext2fs_rename()` mutate directory links.
- `ext2fs_mkdir()` and `ext2fs_rmdir()` manage directory creation/removal and link counts.
- `ext2fs_symlink()` and `ext2fs_readlink()` support fast and block-backed symlinks.
- `ext2fs_pathconf()` reports timestamp resolution and delegates other values to UFS.
- `ext2fs_advlock()` uses inode lockf state.
- `ext2fs_fsync()` flushes buffers and inode metadata.
- `ext2fs_reclaim()` removes inode hash/cache state and returns pools.
- `ext2fsfifo_reclaim()` chains FIFO reclaim to inode reclaim.

Important behavior:
- Immutable and append-only flags affect access, open, setattr, remove, link, rename, mkdir/rmdir contexts.
- Non-root writes that change data clear setuid/setgid in the write path, while chown/chmod enforce BSD ownership rules.
- Rename follows the classic UFS algorithm: temporarily bumps source link count, creates/rewrites target, removes source, and patches `..` for moved directories.
- Directory creation writes `.` and `..` before entering the directory in the parent.
- Fast symlinks shorter than `EXT2_MAXSYMLINKLEN` are stored in the dinode shortlink area.

Dependencies:
- Uses ext2 allocation, directory, inode update/truncate helpers plus generic UFS lock, close, ioctl, kqueue, bmap/strategy, and cache routines.

Watch points:
- Rename has many panic assertions for impossible races or corrupted directory state.
- The FIFO vop table maps `.vop_access` to `ufsfifo_close`, which is an unusual table entry worth checking against surrounding OpenBSD conventions.
