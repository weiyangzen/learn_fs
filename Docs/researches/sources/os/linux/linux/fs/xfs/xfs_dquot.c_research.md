# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot.c

Implements in-core XFS dquot allocation, cache lookup, on-disk read/allocation, limit/timer adjustment, flush, buffer attachment, reference release, locking, and slab lifecycle.

Key behavior:
- Defines dquot lock ordering: inode lock, quota tree lock, dquot lock, flush completion, LRU lock; multiple dquots are ordered by ID.
- Applies default limits and grace periods, computes speculative preallocation thresholds, and manages soft/hard limit timers.
- `xfs_qm_init_dquot_blk` initializes a quota chunk on disk and logs or orders the buffer depending on quotacheck state.
- `xfs_dquot_disk_read` maps quota inode extents and reads the dquot buffer; `xfs_dquot_disk_alloc` allocates missing quota chunks transactionally.
- `xfs_qm_dqread`, `xfs_qm_dqget`, `xfs_qm_dqget_inode`, and `xfs_qm_dqget_next` implement uncached/cache-backed dquot retrieval.
- Cache insertion uses `memalloc_nofs_save` to avoid reclaim recursion while holding quota tree locks.
- `xfs_qm_dqflush` validates in-core quota state, copies it to disk, updates LSN/CRC, attaches the dquot log item to buffer I/O completion, and forces the log if the buffer is pinned.
- Buffer attachment helpers let transaction precommit retain a dquot buffer so AIL pushing can flush without allocating in reclaim context.

This file is the main quota metadata runtime implementation and coordinates tightly with dquot log items, AIL push, quota inode mapping, buffer verifiers, and filesystem health reporting.
