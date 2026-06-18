# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_quota.h

## Role

Defines UFS disk quota file format, in-core dquot cache entries, quota locking order, quota ioctl ABI, and kernel quota helper prototypes.

## Key Structures

- `struct dqblk` is the on-disk quota record indexed by UID. It stores hard/soft block limits, current blocks, hard/soft file limits, current files, and grace-period expiration times.
- `struct dquot` is an in-core quota entry with hash/free links, flags, reference count, UID, owning `ufsvfs`, master disk offset, embedded `dqblk`, and kernel mutex.
- `struct dqhead` is the kernel hash-chain header.
- `struct quotctl` and `struct quotctl32` are ioctl payloads for native and ILP32 callers.

## Constants and Flags

Defines default block/file grace periods of one week, `dqoff(uid)`, dquot flags (`DQ_ERROR`, `DQ_MOD`, `DQ_BLKS`, `DQ_FILES`, `DQ_TRANS`), mount quota flag `MQ_ENABLED`, hash sizing, quota commands (`Q_QUOTAON`, `Q_QUOTAOFF`, `Q_SETQUOTA`, `Q_GETQUOTA`, `Q_SETQLIM`, `Q_SYNC`, `Q_ALLSYNC`), and ioctl command `Q_QUOTACTL`.

## Locking and Interfaces

Documents quota lock order beginning with `vfs_dqrwlock`, then inode contents, dquot cache lock, dquot lock, and free lock. Kernel prototypes cover quota initialization, inode quota lookup, block/inode checks, release/update/invalidation, sync, disk quota lookup, close, and ioctl handling.

## Risk Notes

Quota code is heavily lock-order constrained and participates in logging transactions. Violating the documented order risks deadlock with inode updates and quota enable/disable quiescence.
