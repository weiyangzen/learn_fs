# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vnops.c

FFS vnode operation table and fsync wrapper, with read/write implementations included from shared UFS code.

Key responsibilities:
- Defines normal-file vnode operations for FFS, using UFS defaults plus FFS-specific fsync, block allocation, block reallocation, read, write, getpages, and putpages hooks.
- Defines special-device and FIFO vnode operation tables that use UFS default behavior and FFS fsync.
- Includes `ufs_readwrite.c`, which supplies the `ffs_read()` and `ffs_write()` implementations referenced by the vnode ops table.
- Implements `ffs_fsync()` to flush softdep metadata for mounted block devices, run `vfsync()` with dependency deferral and `softdep_sync_metadata`, then update the inode.
- Implements `ffs_checkdeferred()` to mark buffers with outstanding rollback-causing dependencies as deferred during sync traversal.

Dependencies:
- Uses VM, vnode, buffer, mount, process, and device infrastructure.
- Depends on local `quota.h`, `inode.h`, `ufsmount.h`, `ufs_extern.h`, `fs.h`, and `ffs_extern.h`.
- Calls `softdep_fsync_mountdev()`, `softdep_sync_metadata()`, `vfsync()`, `buf_countdeps()`, and `ffs_update()`.

Notable risks:
- `ffs_fsync()` relies on `vfsync()` callbacks to avoid writing metadata buffers before softdep dependencies are safe.
- Included source `ufs_readwrite.c` means apparent function definitions are split across files; build and review tooling must account for textual inclusion.
- Deferred buffer marking depends on `B_DEFERRED` and dependency counts to prevent premature writes.
