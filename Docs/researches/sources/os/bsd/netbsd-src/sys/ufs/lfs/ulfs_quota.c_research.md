# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.c

Read completely: 1005 lines.

Provides the shared ULFS/LFS quota layer: quota syscall dispatch, common inode quota attachment, dquot cache management, and quota1/quota2 mode selection.

Shared state:
- Global `lfs_dqlock` protects the dquot hash table and reference counts.
- `lfs_dqcv` coordinates quota open/close transitions.
- `dqhashtbl` caches `struct dquot` objects by quota vnode and id.
- `dquot_cache` is the pool cache backing dquot allocations.
- `lfs_quotatypes` names user and group quotas.

Inode integration:
- `ulfsquota_init()` initializes inode dquot pointers to `NODQUOT`.
- `ulfsquota_free()` releases all inode dquot references.
- `lfs_getinoquota()` avoids quota recursion on quota files, maps an inode's uid/gid to user/group dquots, drops stale dquots when ownership changes, and lazily attaches missing dquots.
- `lfs_chkdq()` and `lfs_chkiq()` skip snapshots, then dispatch block/file accounting changes to quota1 or quota2 depending on `fs->um_flags`.

Quotactl dispatch:
- `lfsquota_handle_cmd()` dispatches `QUOTACTL_STAT`, id/object type stat, quota on/off, get/put/delete, and quota2 cursor operations.
- Authorization is handled before mutation: ordinary users may get their own quota, while management/onoff/cursor operations use `kauth_authorize_system()`.
- `quota_handle_cmd_stat()` reports implementation name and restrictions. Quota1 reports 32-bit/uniform grace/needs-check restrictions; quota2 reports no restrictions.
- Delete and cursor operations are quota2-only.
- Quota on/off operations are quota1-only when quota2 is not active.

Dquot cache:
- `lfs_dqinit()`, `lfs_dqreinit()`, and `lfs_dqdone()` initialize, resize, and destroy locks, hash table, CV, and pool cache.
- `lfs_dqget()` validates quota mode and quota vnode availability, checks cache, handles races by rechecking after allocation, inserts a new dquot, and invokes `lfs_dq1get()` or `lfs_dq2get()` to populate format-specific state.
- `lfs_dqrele()` decrements references, synchronizes modified dquots before final release, removes final dquots from the hash, destroys their interlock, and returns them to the pool.
- `lfs_qsync()` dispatches sync to quota1 or quota2.

Risks and notes:
- Lock order is important: comments in `ulfs_quota.h` state `dq_interlock -> dqlock` and `dq_interlock -> dqvp`.
- Several impossible dispatch cases panic with “no support ?”.
- Quota2 `lfs_q2sync()`/`lfs_dq2sync()` are stubs because quota2 updates write metadata buffers directly.
- Snapshot accounting is deliberately skipped to avoid deadlocks.
