# File Research: sources/os/linux/linux/fs/xfs/xfs_icache.c

Implements the XFS in-core inode cache: inode allocation/freeing, `iget`, reclaim tagging, inode cache walks, speculative block garbage collection, deferred inode inactivation, and inodegc shrinker integration.

Key elements:
- Maintains per-AG radix-tree inode caches with tags for reclaimable inodes and inodes needing EOF/COW block cleanup; tags are propagated into per-group xarray marks.
- `xfs_inode_alloc` initializes the embedded VFS inode and XFS inode fields, forks, work items, mapping folio order, and unlinked-list state.
- Freeing uses RCU and clears inode number/state before release so concurrent RCU cache lookups can detect recycled or freed objects.
- `xfs_iget` validates inode numbers, handles cache hits/misses, recycles reclaimable inodes, reads inode cores from disk when needed, inserts new inodes into the per-AG radix tree, and returns requested inode locks.
- Cache-hit handling avoids inodes under construction, reclaim, inactivation, or incomplete inactive cleanup; it can queue inodegc and retry when necessary.
- `xfs_trans_metafile_iget` and `xfs_metafile_iget` validate metadata inode mode, link count, metadir membership, and metafile type.
- Reclaim logic grabs eligible reclaimable inodes, avoids sick inodes unless unmount/norecovery/shutdown requires it, flushes AIL as needed, removes inodes from the radix tree, and frees them after coordination with lookup races.
- Inode-cache walking batches tagged radix-tree lookups per AG and dispatches per-goal processing for reclaim or block garbage collection.
- Blockgc tags and workers release speculative post-EOF blocks and pending COW reservations, with quota/id/min-size filtering and sync/async behavior.
- Inodegc queues inodes needing inactive processing onto per-CPU lockless lists, schedules delayed work based on backlog/free-space/quota pressure, and can be pushed/flushed/stopped/started.
- Inodegc worker runs `xfs_inactive`, marks inodes reclaimable, tracks errors, and uses NOFS allocation context.
- A phony shrinker accelerates inodegc under memory pressure and can throttle frontend queuing when shrinker-triggered backlog exists.

Dependencies:
- Uses radix trees, xarrays, RCU, per-CPU state, delayed workqueues, shrinkers, lockless lists, VFS inode lifecycle, quota, reflink/COW, bmap utilities, AIL/log state, XFS per-AG groups, health state, and metadata inode helpers.

Research notes:
- Inode lookup and reclaim rely heavily on `i_flags_lock`, ILOCK, radix-tree tags, and RCU ordering to avoid use-after-free during cache walks.
- Reclaim does no normal metadata I/O; callers needing clean inodes must push the AIL first.
- Blockgc avoids freeing COW staging extents under dirty/writeback/direct-I/O conditions because completion paths rely on those reservations.
- Inodegc is separate from reclaim because inactive processing can require transactions and metadata updates before memory can be reclaimed.
