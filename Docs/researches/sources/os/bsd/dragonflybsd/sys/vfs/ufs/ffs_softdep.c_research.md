# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep.c

DragonFly UFS/FFS soft updates implementation. It tracks metadata dependencies so UFS can issue asynchronous writes while preserving crash-safe ordering for allocation bitmaps, inode blocks, indirect blocks, directory entries, truncation, and inode reuse.

Key responsibilities:
- Registers a `bio_ops` implementation for softdep-aware buffer lifecycle hooks: I/O initiation, write completion, dependency deallocation, vnode fsync, mount sync, dependency movement/counting, and read/write checks.
- Maintains dependency objects for pages/directories (`pagedep`), inodes (`inodedep`), newly allocated blocks (`newblk`), cylinder-group bitmap safety (`bmsafemap`), direct and indirect allocations (`allocdirect`, `allocindir`, `indirdep`), delayed fragment/block/file frees, mkdir dependencies, directory additions, and directory removals.
- Builds hash tables for pagedep, inodedep, and newblk lookups, with simple semaphores to serialize racing structure creation.
- Protects allocation bitmaps by attaching inode/block allocation dependencies to cylinder-group buffers and completing them only after bitmap buffers reach disk.
- Handles direct block allocation dependencies, including fragment replacement, old-fragment delayed free, ordered inode dependency lists, directory page dependency creation, and merge handling for repeated allocation to the same logical block.
- Handles indirect block allocation dependencies by maintaining a safe shadow copy of indirect blocks; pending unsafe pointers are rolled back before disk writes and restored afterward.
- Implements truncate-to-zero and file deletion dependency handling: zeroes inode pointers, drains dirty buffers, deallocates obsolete dependencies, then delays block and inode frees until the zeroed inode state is stable.
- Implements directory add/remove/change ordering: new directory entries wait for target inode updates, removals wait for directory blocks to commit, renames combine add and remove dependencies, and mkdir adds also wait for `.`/`..` body and parent link updates.
- Rolls metadata back during `softdep_disk_io_initiation()` and rolls it forward during `softdep_disk_write_complete()`, marking buffers dirty again when an unsafe write used a temporary safe image.
- Provides synchronous cleanup paths used by `fsync`, sync, unmount, and memory-pressure throttling: `softdep_fsync`, `softdep_sync_metadata`, `softdep_flushfiles`, `flush_inodedep_deps`, `flush_pagedep_deps`, `clear_remove`, and `clear_inodedeps`.
- Recomputes cylinder-group summaries on softdep mount if the filesystem was not clean, because soft updates guarantees bitmap ordering more directly than auxiliary summary counters.

Dependencies:
- Includes DragonFly kernel buffer, mount, vnode, lock, spinlock, sysctl, and bio infrastructure.
- Depends on local UFS headers: `dir.h`, `quota.h`, `inode.h`, `ufsmount.h`, `fs.h`, `softdep.h`, `ffs_extern.h`, and `ufs_extern.h`.
- Calls core UFS/FFS routines including `ffs_flushfiles`, `ffs_blkfree`, `ffs_freefile`, `ffs_truncate`, `ffs_update`, `VFS_VGET`, `VOP_FSYNC`, `bread`, `bwrite`, `bawrite`, and buffer cache helpers.

Notable risks:
- The file intentionally enables `DIAGNOSTIC` and `DEBUG` if absent, reflecting the fragility of dependency invariants and the value of runtime checks.
- There is a likely typo in `newblk_lookup()` race cleanup: it releases `pagedep_in_progress` instead of `newblk_in_progress`.
- Locking is complex: many paths drop and reacquire the global softdep lock around allocation, I/O, vnode lookup, or buffer locking; callers must respect buffer/vnode lock ordering to avoid races or deadlocks.
- Several fatal paths use `panic()` for invariant violations or unrecovered I/O errors, so corrupt dependency state is treated as kernel-fatal rather than recoverable.
- The implementation only handles the common softdep truncation case of reducing file length to zero; other truncation cases are left to synchronous write behavior.
- Memory-pressure mitigation is heuristic, driven by `max_softdeps`, worklist backlog, syncer requests, and timed sleeps.
