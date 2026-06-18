# File Research: sources/os/linux/linux/fs/xfs/xfs_inode.c

Implements core XFS inode operations: inode locking, namespace operations, inode creation/deletion, inactive cleanup, unlinked-list recovery, inode flushing, layout breaking, and inode utility helpers.

Key elements:
- Provides lock helpers for IOLOCK, MMAPLOCK, and ILOCK with documented ordering, trylock rollback, demotion, lockdep subclassing, and assertions.
- Implements multi-inode locking in inode-number order for rename/remap-style operations, with AIL-aware trylock retries to avoid log-tail deadlocks.
- `xfs_lookup` resolves directory entries, igets target inodes, handles case-insensitive names, and rejects metadata inodes reachable from the regular directory tree.
- `xfs_icreate`, `xfs_create`, and `xfs_create_tmpfile` allocate quota resources, reserve transactions, allocate inode numbers, initialize in-core/on-disk inode state, attach dquots, update directories or unlinked lists, and commit.
- `xfs_link`, `xfs_remove`, and `xfs_rename` implement namespace updates with quota attachment, parent pointer support, project-id inheritance checks, whiteout support, reservation fallback, AGI lock ordering, and synchronous-mount behavior.
- Truncation helpers remove blocks past EOF, cancel COW reservations, clear reflink/COW tags when possible, and relog inode core state through rolling transactions.
- Inactive processing handles COW cleanup, EOF block freeing, unlinked regular-file truncation, directory buffer staling, symlink cleanup, attribute fork teardown, inode free, dquot detach, and persistent marking of unresolved inode health.
- `xfs_ifree` returns unlinked inodes to the free list, clears obsolete logged owner fields, and can stale an entire inode cluster buffer when the chunk becomes free.
- Cluster-freeing logic marks all cached inodes in the freed cluster stale and attaches dirty inodes to the stale buffer so journal completion removes them safely.
- Pin helpers force log sequences and wait for inode pin counts to drop.
- `xfs_iflush` validates incore inode state, updates legacy flushiter, verifies local forks, copies dirty state to the on-disk inode buffer, coordinates `ili_fields`/`ili_last_fields`, stores flush LSN, calculates CRC, and marks corrupt cores sick.
- `xfs_iflush_cluster` scans inodes attached to a cluster buffer, nonblockingly flushes eligible dirty inodes, handles shutdown aborts, and fails the buffer/shuts down on corruption.
- Layout helpers break file leases and DAX layouts while obeying VFS inode and XFS MMAPLOCK ordering for two-inode operations.
- Utility helpers reload unrecovered unlinked lists, detect zapped forks, count realtime/data blocks, calculate allocation unit size, and decide always-COW behavior.

Dependencies:
- Uses VFS inode locking/state, XFS directory, bmap, reflink, quota, parent pointers, transactions, defer ops, inode allocation/free, log/AIL, buffer items, symlink/attr cleanup, metadata inode support, DAX/layout lease APIs, and health tracking.

Research notes:
- Namespace removal deliberately drops link counts before removing directory entries to preserve AGI-before-AGF lock ordering.
- Inactive processing is skipped for read-only mounts except recovery, internal metadata inodes, shutdown/norecovery paths, and already-free inodes.
- Inode cluster staling is carefully synchronized with inode flush and reclaim to avoid stale dirty inodes remaining in AIL or memory.
- Flush failure due to corrupt incore state forces shutdown before releasing the buffer so log-tail movement cannot make recovery unsafe.
