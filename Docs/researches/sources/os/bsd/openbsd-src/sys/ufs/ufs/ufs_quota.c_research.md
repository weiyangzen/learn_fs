# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota.c

Read completely: 1100 lines.

Implements UFS disk quota accounting, quotactl operations, and the in-core dquot cache.

Core behavior:
- `struct dquot` caches quota-file records with hash linkage, free-list linkage, flags, type/id, reference count, quota vnode/credentials, and `dqblk` contents.
- `getinoquota()` attaches user and group dquots to an inode based on uid/gid when quotas are enabled.
- Block/inode allocation functions check hard and soft limits for non-root callers, start grace timers, emit user warnings, update usage, and mark dquots modified; free functions decrement usage and clear warning flags.
- `quotaon()` opens a quota file, records vnode/credentials, marks quota state opening, sets default grace times from id 0, attaches dquots to active writable vnodes, and rolls back on error.
- `quotaoff()` marks closing, detaches dquots from mounted vnodes, closes the quota vnode, releases credentials, and clears `MNT_QUOTA` when no quotas remain.
- `getquota()`, `setquota()`, and `setuse()` implement userland quota record fetch/update and ktrace reporting.
- `qsync()` walks vnodes and writes modified dquots.
- `dqget()` hashes by quota vnode and id, reuses free dquots or allocates new ones, reads quota records from the quota file, initializes fake/no-limit and grace-time state, and handles read errors.
- `dqrele()` syncs modified last references and moves unused dquots to the free list; `dqsync()` writes quota records under a dquot lock.
- `ufs_quotactl()` performs privilege checks, mount busy protection, command dispatch, and unbusy cleanup.

Integration and risks:
- Quota state uses ad hoc `DQ_LOCK`/`DQ_WANT` sleep locking; lost wakeups or missed flag clearing would stall accounting.
- Ownership changes in `ufs_chown()` rely on quota free/delete/reallocate rollback semantics.
- Quota file vnodes are marked system files and are accessed through normal vnode read/write paths, so recursion/locking around `dqvp` matters.
