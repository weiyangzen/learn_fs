# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.c

## Purpose
Implements core XFS dquot management: in-core allocation/destruction, on-disk allocation/read, cache lookup/insert, quota defaults/timers, dquot flushing, attached buffer handling, locking helpers, and slab cache setup.

## Main APIs
- `xfs_qm_dqget`, `xfs_qm_dqget_inode`, `xfs_qm_dqget_uncached`, and `xfs_qm_dqget_next` load dquots from cache or disk.
- `xfs_qm_dqrele` releases references and adds unused dquots to the quota LRU.
- `xfs_qm_init_dquot_blk` initializes an on-disk block of dquots.
- `xfs_qm_dqflush` writes an in-core dquot to its backing buffer and wires I/O completion to AIL cleanup.
- `xfs_dquot_attach_buf`, `xfs_dquot_use_attached_buf`, and `xfs_dquot_detach_buf` manage reclaim-safe buffer references for dirty dquots.
- `xfs_dqlock2` and `xfs_dqlockn` provide deadlock-safe multi-dquot locking.
- `xfs_qm_init` and `xfs_qm_exit` create/destroy dquot and transaction-accounting slabs.

## On-Disk Handling
Dquot reads map quota inode file offsets to disk, read dquot chunks with verifiers, and copy one `xfs_disk_dquot` into in-core counters. Holes can be allocated with a quota allocation transaction, initialized as a full dquot chunk, held through commit, and returned locked.

## Limits and Timers
Default limits are applied when non-root dquots have zero limits. Timers start when usage exceeds soft or hard limits and reset when usage returns below limits. Grace periods are clamped. Preallocation watermarks are derived from soft/hard block and realtime-block limits.

## Cache and Locking
Cache lookup uses per-quota-type radix trees and `lockref_get_not_dead` to avoid resurrecting freeing dquots. Insert runs under `memalloc_nofs` to avoid reclaim recursion through quota tree locks. Lock ordering is documented: inode lock, quota tree lock, dquot lock, flush lock, LRU lock; multiple dquots lock by type/id order.

## Flush and AIL Coordination
Flush checks in-core consistency, copies fields to the disk dquot, writes CRC/LSN for CRC filesystems, attaches the log item to the buffer I/O list, and forces the log if the buffer is pinned. I/O completion removes unchanged dquots from the AIL and releases attached buffers/flush locks.

## Failure Handling
Quota metadata verifier errors mark the corresponding quota health flag sick. Flush corruption forces shutdown before deleting the AIL item to avoid unrecoverable log-tail advancement.
