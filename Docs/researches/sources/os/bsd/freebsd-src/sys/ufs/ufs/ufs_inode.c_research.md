# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_inode.c

## Purpose
Implements UFS inode lifecycle vnode operations: deciding whether inactive processing is required, handling the last vnode reference, and reclaiming inode memory/state.

## Key entry points
- `ufs_need_inactive()` decides whether `VOP_INACTIVE` must run. It skips read-only inodes, but requests inactive processing for pending page-queue flushes, deleted/unlinked inodes, softdep-effective unlink state, dirty inode flags, non-empty deleted files including UFS2 extended data, and attached quota references.
- `ufs_inactive()` performs last-reference cleanup. It handles quota sync, GEOM journal close, suspended-write coordination, truncation of unlinked files, quota inode accounting release, extended-attribute inactive cleanup, inode mode clearing, block/inode freeing through `UFS_VFREE`, timestamp updates, and vnode recycling.
- `ufs_reclaim()` tears down the in-core inode: releases dquots, frees directory hash state, promotes lazy modification to real modification, updates the inode, removes the vnode from the hash, clears `v_data` under the vnode interlock, and frees the inode through `UFS_IFREE`.

## Important behavior
- File deletion is split across truncation, link-count state, soft updates, and final inode free. `i_effnlink` is significant under soft updates, while `i_nlink` is the on-disk link count.
- `vn_start_secondary_write()` protects deletion/truncation against filesystem suspension. If the filesystem is suspended and the vnode is not doomed, `VI_OWEINACT` is set so inactive work can be retried later.
- UFS2 extended size contributes to the deletion truncation decision via `di_extsize`.
- Quotas are synchronized before inactive vnodes leave the active list, because inactive quota state is otherwise no longer checked.

## Dependencies
Uses UFS operation indirection from `ufsmount.h`: `UFS_RDONLY`, `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_VFREE`, `UFS_IFREE`. Optional paths depend on `QUOTA`, `UFS_DIRHASH`, `UFS_EXTATTR`, `UFS_GJOURNAL`, and soft updates.

## Research notes
This file is the cleanup boundary for UFS vnode lifetime. Most actual allocation, truncation, update, and free behavior is delegated to filesystem-specific callbacks, allowing common UFS code to serve UFS1/UFS2 and FFS-specific implementations.
