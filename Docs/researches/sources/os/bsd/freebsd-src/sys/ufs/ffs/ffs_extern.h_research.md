# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_extern.h

Kernel-only external interface for the FreeBSD FFS implementation.

Key content:
- Declares allocation/free APIs: `ffs_alloc`, UFS1/UFS2 `ffs_balloc`, `ffs_blkfree`, block preference helpers, TRIM release key helpers, `ffs_realloccg`, `ffs_reallocblks`, inode allocation/free, `ffs_freefile`, `ffs_checkfreefile`, and cylinder-group helpers.
- Declares superblock and mount operations: superblock hash, search/get/put/update, reload, mount ownership check, old filesystem compatibility helpers, file flush, sync vnode, snapshot mount/unmount/sync/remove, suspension init/uninit, and fsfail cleanup helpers.
- Declares vnode lookup/get APIs: `ffs_vget`, `ffs_vgetf`, `ffs_inotovp`.
- Defines `ffs_vgetf` flags for forced mount-list insertion, replacement, doomed replacement, forced inode dependency, and newly allocated inode handling.
- Defines `ffs_reload` flags for force and unsuspend.
- Defines TRIM keys: `NOTRIM_KEY`, `SINGLETON_KEY`, `FIRST_VALID_KEY`, and `MAXTRIMIO`.
- Exports vnode operation vectors for UFS1/UFS2 regular and FIFO vnode ops.
- Declares the soft updates API surface used throughout FFS allocation, inode updates, sync, rename/link prechecks, block/inode dependency setup, journal handling, buffer dependency movement, cleanup requests, and worklist management.
- Defines softdep cleanup request constants for inode/block flushing with optional wait.
- Defines `ffs_syncvnode()` flags `NO_INO_UPDT` and `DATA_ONLY`.
- Declares `ffs_rdonly()` and snapshot data structures.

Research relevance:
- This is the FFS subsystem contract file tying allocation, vnode ops, mount/superblock handling, snapshots, and soft updates together.
- It is the quickest index of cross-file dependencies for FFS implementation work.
