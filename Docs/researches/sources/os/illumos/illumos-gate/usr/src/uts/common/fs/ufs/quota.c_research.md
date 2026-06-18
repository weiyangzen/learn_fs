# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota.c

## Purpose

`quota.c` manages UFS in-core dquot structures: initialization, hash/free-list caching, lookup/loading from the on-disk quota file, release/writeback, and invalidation when quotas are disabled or a filesystem unmounts.

## Main Interfaces

The file provides `qtinit`, `qtinit2`, `getdiskquota`, `dqput`, `dqupdate`, `dqinval`, and `invalidatedq`.

## Behavior And Data Flow

`qtinit()` initializes the global quota subsystem rwlock. `qtinit2()` allocates the dquot table on first quota use, initializes hash heads and the free list, and creates per-dquot mutexes.

`getdiskquota()` requires the filesystem quota rwlock, checks whether quotas are enabled unless forced, looks up the `(uid, ufsvfs)` dquot in the hash cache, and otherwise reuses a free dquot. It reads `struct dqblk` from the quota inode when the uid offset is valid, records the master offset for later logging, handles quota-file I/O errors by removing the dquot from the cache, and returns the dquot referenced.

`dqput()` decrements the reference count. Last release writes modified quota data with `dqupdate()`, clears flags, and either invalidates the dquot if quotas are disabled or returns it to the free list.

## Logging Integration

`dqupdate()` writes modified quota data either through UFS logging or directly to the quota inode. If the caller is not already in a transaction, it temporarily sets `T_DONTBLOCK`, starts an async `TOP_QUOTA` transaction, logs a `DT_QR` delta and quota record, then ends the transaction. Non-logging updates write with `ufs_rdwri()` under the quota inode contents lock.

## Invalidation And Locking

`dqinval()` removes a zero-reference dquot from its hash chain and returns it to the head of the free list, temporarily clearing `dq_ufsvfsp` to avoid lookup races while lock order is adjusted. `invalidatedq()` scans all dquots for a filesystem after quotas are disabled, skipping transient `DQ_TRANS` records that logging still owns.

Global cache/free-list locks protect hash and free-list mutation, while per-dquot locks protect object fields. The filesystem `vfs_dqrwlock` is required around most external quota operations.

## Notable Risks

High-risk areas are lock-order transitions between `dq_cachelock`, `dq_freelock`, `dq_lock`, and `vfs_dqrwlock`; quota I/O error cleanup; `DQ_TRANS` orphan handling during unmount; and ensuring logged quota deltas release dquot references through the logging map layer.
