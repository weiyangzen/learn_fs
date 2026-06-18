# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vnops.c

Read completely: 545 lines.

Defines FFS vnode operation vectors and implements FFS-specific regular-file I/O, fsync, and inode reclaim.

Core behavior:
- `ffs_vops`, `ffs_specvops`, and optional `ffs_fifovops` bind generic UFS directory/metadata operations to FFS read/write/fsync/reclaim behavior, plus special-device and FIFO wrappers.
- `ffs_read()` validates offsets/types, reads logical file blocks with `bread()` or clustered read-ahead, clamps transfers to file size and residual I/O, and marks access time unless `MNT_NOATIME` suppresses it.
- `ffs_write()` enforces append-only and max-file-size/rlimit checks, allocates blocks through `UFS_BUF_ALLOC()`, extends vnode size, clears exposed buffer contents on failed partial `uiomove()`, chooses sync/async/delayed writes, clears setuid/setgid for unprivileged successful writes, and rolls back `IO_UNIT` writes by truncating to the original size.
- `ffs_fsync()` scans dirty vnode buffers under `splbio()`, skips metadata on the first synchronous pass, writes dirty buffers, waits for vnode I/O, retries dirty buffers for non-block devices, and finally calls `UFS_UPDATE()`.
- `ffs_reclaim()` delegates generic UFS cleanup, returns UFS1/UFS2 dinodes and inode objects to pools, and clears `v_data`; `ffsfifo_reclaim()` chains FIFO cleanup first.

Integration and risks:
- Depends on `inode.h` `DIP()` and vnode vtable indirection to support UFS1/UFS2.
- Buffer state flags and `splbio()` ordering are critical in `ffs_fsync()`.
- Write error cleanup is subtle because newly instantiated pages must not expose stale data through mmap.
