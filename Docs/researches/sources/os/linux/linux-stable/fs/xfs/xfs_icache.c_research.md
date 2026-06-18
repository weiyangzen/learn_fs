# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_icache.c

## Purpose

Implements XFS in-core inode cache management, inode lookup/recycling, reclaim, speculative preallocation garbage collection, deferred inode inactivation, and inode-cache walking.

## Main Responsibilities

- Allocates and initializes `struct xfs_inode` objects through `xfs_inode_alloc`.
- Frees inodes through RCU-safe teardown and fork/log-item cleanup.
- Performs `xfs_iget` cache lookup, cache miss loading, reclaimable-inode recycling, and metadata inode validation.
- Maintains per-AG radix-tree tags for reclaimable inodes and blockgc candidates.
- Runs inode reclaim workers and shrinker-driven reclaim scans.
- Runs blockgc scans to free post-EOF and COW speculative preallocations.
- Queues and drains deferred inode inactivation work through per-cpu `xfs_inodegc` lists.
- Registers a shrinker that accelerates inodegc under memory pressure.

## Key Data Structures

- Per-AG inode radix tree: `pag->pag_ici_root`
- Inode cache tags:
  - `XFS_ICI_RECLAIM_TAG`
  - `XFS_ICI_BLOCKGC_TAG`
- Per-AG xarray marks:
  - `XFS_PERAG_RECLAIM_MARK`
  - `XFS_PERAG_BLOCKGC_MARK`
- `struct xfs_icwalk`
  - Public/private scan filters for uid, gid, project id, minimum file size, sync mode, scan limits, reclaim-sick mode, and union matching.

## Inode Lookup Flow

`xfs_iget` verifies the inode number, finds the per-AG object, and looks in the radix tree under RCU:

- Cache hit: `xfs_iget_cache_hit`
  - Rejects stale RCU entries, inodes under construction, inactivation, or reclaim.
  - Flushes inodegc when a referenced inode still needs inactivation.
  - Recycles reclaimable inodes with `xfs_iget_recycle`.
  - Grabs live VFS inodes with `igrab`.
  - Checks free/allocated state against `XFS_IGET_CREATE`.
- Cache miss: `xfs_iget_cache_miss`
  - Allocates an inode, maps it, reads the ondisk dinode unless creating a v3 inode, validates free state, and inserts it into the per-AG radix tree.

`xfs_trans_metafile_iget` and `xfs_metafile_iget` layer metadata-file type, nlink, mode, and metadir checks on top of `xfs_iget`.

## Reclaim Flow

- `xfs_inode_mark_reclaimable` chooses between deferred inactivation and direct reclaim.
- `xfs_inodegc_set_reclaimable` sets `XFS_IRECLAIMABLE` and the reclaim radix-tree tag.
- `xfs_reclaim_inode` grabs reclaim candidates, avoids dirty/pinned inodes, handles log shutdown by aborting flush state, removes the inode from the radix tree, and frees it after lookup synchronization.
- `xfs_reclaim_inodes`, `xfs_reclaim_inodes_nr`, and `xfs_reclaim_worker` drive reclaim from unmount, shrinkers, and background work.

## Blockgc Flow

- `xfs_inode_set_eofblocks_tag` and `xfs_inode_set_cowblocks_tag` set inode flags and per-AG blockgc tags.
- `xfs_inode_free_eofblocks` frees post-EOF space when the inode matches scan filters and can be safely locked.
- `xfs_inode_free_cowblocks` cancels COW fork reservations only when writeback/direct I/O hazards are excluded and IO/MMAP locks can be taken.
- `xfs_blockgc_worker`, `xfs_blockgc_free_space`, `xfs_blockgc_flush_all`, `xfs_blockgc_free_dquots`, and `xfs_blockgc_free_quota` provide background, synchronous, and quota-pressure entry points.

## Inodegc Flow

- `xfs_inodegc_queue` marks an inode `XFS_NEED_INACTIVE`, pushes it to a per-cpu lockless list, and schedules work based on cluster-size backlog, low free space, realtime low space, quota pressure, or shrinker pressure.
- `xfs_inodegc_worker` runs in NOFS context, sets `XFS_INACTIVATING`, calls `xfs_inactive`, and moves the inode to reclaimable state.
- `xfs_inodegc_push`, `xfs_inodegc_flush`, `xfs_inodegc_stop`, and `xfs_inodegc_start` control draining and enablement.
- The inodegc shrinker does not directly free memory; it schedules inactivation so later reclaim can free inodes.

## Important Invariants

- Inode numbers are set to zero before RCU freeing so cache lookups can detect stale or reused entries.
- Reclaim and blockgc tag state is mirrored from inode radix-tree tags into per-AG xarray marks.
- Reclaim must not perform ordinary writeback; callers push the AIL first if dirty inode metadata must be cleaned.
- Sick inodes are not reclaimed unless unmount, no-recovery, or shutdown conditions make that appropriate.
- Blockgc does not free COW staging extents for files with unsafe writeback or direct I/O state.
- Deferred inactivation is disabled/drained under `sb->s_umount` coordination.

## Dependencies

This file integrates with inode formatting/loading, quota, bmap utilities, reflink, AG group iteration, log/AIL pushing, health tracking, metadata-file validation, workqueues, shrinkers, radix trees, and RCU.

## Research Notes

This is the coordination center for XFS inode memory lifecycle. The hardest parts are the state transitions among `XFS_INEW`, `XFS_NEED_INACTIVE`, `XFS_INACTIVATING`, `XFS_IRECLAIMABLE`, `XFS_IRECLAIM`, `XFS_IFLUSHING`, and `XFS_ISTALE`, all of which protect against lookup, reclaim, flush, and free races.
