# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_subr.c

## Overview
`ufs_subr.c` contains shared UFS support routines for mount-instance list management, global sync/update work, inode and indirect-block flushing, clean-state transitions, superblock/summary-info I/O, sticky-directory permission checks, and traditional UFS fragment/block bitmap helpers.

## Main Responsibilities
- Maintain the global `ufs_instances` list with `ufs_vfs_add()` and `ufs_vfs_remove()`.
- Clean delayed forced-unmount `ufsvfs` structures through `ufs_funmount_cleanup()`.
- Implement `ufs_update()` for global UFS sync processing.
- Flush inode data and metadata via `ufs_sync_inode()`, `ufs_syncip()`, `ufs_sync_indir()`, and `ufs_indirblk_sync()`.
- Decide when a filesystem can be marked stable through `ufs_checkclean()`.
- Mark logging filesystems as needing reclaim after unlink with `ufs_setreclaim()`.
- Mark filesystems dirty/active before metadata writes with `ufs_notclean()`.
- Write file blocks, inode blocks, superblocks, and cylinder group summary information.
- Provide fragment accounting and allocation bitmap helpers used by kernel and non-kernel UFS code.

## Sync and Clean-State Flow
- `ufs_update()` builds a temporary list of mounted UFS instances it can `vfs_lock()`, writes modified superblocks, scans inodes, flushes buffers, and then rechecks stable candidates.
- It avoids writing locked/inconsistent superblocks during panic and skips panicking/logging cases where metadata should not be forced out.
- `ufs_sync_inode()` applies cheap-sync filtering, panic filtering, deferred access-time policy, and then either delays inode update or flushes pages through `TRANS_SYNCIP()`.
- `ufs_syncip()` flushes vnode pages and then updates inode metadata according to full-sync versus data-sync semantics.
- `ufs_checkclean()` marks the filesystem `FSSTABLE` only when buffers and inodes are not busy and reclaim state allows it.

## Metadata and Summary Information
- `ufs_sbwrite()` updates `fs_time`, `fs_state`, `fs_clean`, and reclaim bits, logs the superblock delta, writes the superblock buffer, and preserves the in-core `fs_fmod` value.
- `ufs_getsummaryinfo()` either reads summary info from the summary-info area or reconstructs it from cylinder groups when `FS_SI_BAD`.
- `ufs_construct_si()` performs batched asynchronous reads of cylinder groups and copies each `cg_cs`.
- `ufs_putsummaryinfo()` writes summary info back when logging needs it and `vfs_nolog_si` permits delayed summary flushing.
- `still_mounted()` verifies that a stored check node still refers to an active instance before clean-state checking.

## Indirect Block Handling
- `ufs_sync_indir()` flushes all indirect blocks associated with a file, including single, double, and triple indirect levels.
- `ufs_indirblk_sync()` flushes the indirect path needed for a specific file offset.
- Both skip work when logging is enabled because allocation metadata is kept current by transactions.
- Debug-only `ufs_badblock()` and `ufs_indir_badblock()` can validate block-number ranges when the expensive tunable is enabled.

## Fragment and Block Helpers
- `fragacct()` updates fragment summary counts using `fragtbl`, `around`, and `inside` tables from `ufs_tables.c`.
- `isblock()`, `clrblock()`, `isclrblock()`, and `setblock()` manipulate free block maps for fragment sizes 1, 2, 4, and 8.
- `skpc()` scans past a repeated character and returns remaining length.

## Locking and Safety
- `ufsvfs_mutex` protects UFS instance lists.
- `ufs_scan_lock` avoids races among update, sync, and unmount inode scans.
- `vfs_lock()` pins a filesystem instance for update work.
- `vfs_lock`, `vfs_lockp`, `i_contents`, `i_tlock`, and `vfs_dqrwlock` are used according to the specific inode/superblock/quota operation.
- Forced-unmount cleanup intentionally delays freeing some `ufsvfs` objects to reduce races with lockfs users.

## Research Notes
This file is the common maintenance layer for UFS consistency. Its riskiest areas are global instance traversal without long-held list locks, clean-state decisions, summary-info reconstruction, and the split behavior between logging and non-logging filesystems.
