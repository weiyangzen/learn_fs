# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quotacalls.c

This file implements UFS quota control operations behind `quotactl`: turning quotas on and off, setting limits, reading limits, and syncing quota records. It also owns the global `quotas_initialized` flag.

`quotactl` copies in the native or ILP32 `quotctl` structure, defaults negative UIDs to the caller's real UID, resolves the target `ufsvfs` except for all-filesystem sync cases, then dispatches `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_SETQUOTA`, `Q_SETQLIM`, `Q_GETQUOTA`, `Q_SYNC`, and `Q_ALLSYNC`. Quota initialization is protected by the global `dq_rwlock`.

`opendq` enables quotas for one mounted UFS filesystem. It requires quota privilege, holds the quota vnode, validates it is a regular file, then takes `vfs_dqrwlock` as writer to quiesce quota state. For a newly enabled filesystem it installs `vfs_qinod`, expands the quota file to at least `fs_bsize * NDADDR` to avoid partial fragment relocation, marks metadata, loads uid 0's quota record as the source of block and file grace defaults, sets `MQ_ENABLED`, updates mount options, and scans all cached inodes to attach dquots. If quotas were already enabled, it accepts only the same quota inode and otherwise warns that the previous quota file remains in use.

`closedq` disables quotas. Under `vfs_dqrwlock` writer it clears `MQ_ENABLED`, updates mount options, scans cached inodes to detach `i_dquot`, cancels pending logging quota transactions by clearing `DQ_TRANS` and dropping the extra reference, clears `vfs_qinod`, then syncs and releases the quota inode outside the quota rwlock.

`setquota` changes quota records. It requires privilege and enabled quotas, copies in a `dqblk`, preserves current usage for `Q_SETQLIM`, updates filesystem grace defaults when setting uid 0, and otherwise adjusts user grace timers and warning flags depending on whether usage crosses soft limits. It detects transitions from no limits to any limits, or from some limits to no limits, and scans cached inodes for that UID to attach or detach their dquot pointers accordingly. It writes the updated quota record to the quota file synchronously and computes `dq_mof` with `bmap_read` for logging metadata-offset tracking.

`getquota` allows users to read their own quota and requires quota privilege for other UIDs. It returns `ESRCH` if quotas are disabled or the record has no limits, otherwise copies the `dqblk` to user space.

`quotasync` flushes modified dquot records for one filesystem or all quota-enabled filesystems. It is a no-op for logging filesystems because quota state is treated as metadata in the log. For all-filesystem sync it uses `mutex_tryenter` and `rw_tryenter` to avoid deadlock with the normal `vfs_dqrwlock > dq_lock` order, skipping records it cannot safely lock.

Integration notes: the control path centers on `vfs_dqrwlock` as a filesystem-level quota quiescing mechanism. Cached inode dquot pointers are deliberately repaired after quota-on and limit/no-limit transitions. Sync paths may skip busy dquots rather than block in unsafe lock order.
