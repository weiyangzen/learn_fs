# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_readwrite.c

## Purpose

Implements FFS/UFS vnode read and write operations for regular files, directories, and long symlinks.

## Main Functions

- `ffs_read(struct vop_read_args *ap)`: reads file data through the buffer cache with read-ahead, EOF clipping, optional direct I/O buffer release, and atime marking.
- `ffs_write(struct vop_write_args *ap)`: writes file data through `VOP_BALLOC()`, handles append mode, immutable append enforcement, file size/resource limits, VM object size updates, buffer clearing, clustering, direct I/O, synchronous/asynchronous writes, setuid/setgid clearing, and timestamp updates.

## Important Read Behavior

Reads validate type under `DIAGNOSTIC`, reject offsets beyond `fs_maxfilesize`, stop at EOF, use `ffs_blkatoff_ra()` with sequence hints, and never copy past initialized buffer data. Buffers without dependencies may be marked `B_RELBUF` for VM/direct I/O.

## Important Write Behavior

Writes enforce `APPEND`, `fs_maxfilesize`, and `RLIMIT_FSIZE`. Before extending the file, the VM object size is updated via `nvnode_pager_setsize()`. Partial-block writes and no-copy writes use `B_CLRBUF` to avoid exposing stale data. Buffer writeback policy chooses among synchronous `bwrite()`, async `bawrite()`, clustered `cluster_write()`, direct-I/O async write, or delayed `bdwrite()`.

`IO_UNIT` error handling rolls the file back to its original size and restores the user I/O offset/residual.

## Dependencies And Integration Points

Uses FFS macros and functions including `blksize`, `lblkno`, `blkoff`, `blkoffresize`, `VOP_BALLOC`, `ffs_blkatoff_ra`, `ffs_truncate`, `ffs_update`, and `ufs_itimes()`. Emits vnode write/extend knotes via `VN_KNOTE`.

## Notes For Future Work

- `UIO_NOCOPY` sets `IN_NOCOPYWRITE` and interacts with `VLASTWRITETS` timestamp handling in `ufs_itimes()`.
- The file aliases generic macro names (`FS`, `I_FS`, `BLKSIZE`) to FFS/UFS-specific fields before including VM/buffer headers.
