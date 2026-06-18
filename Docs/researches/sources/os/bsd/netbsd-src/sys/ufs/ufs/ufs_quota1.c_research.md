# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota1.c

This file implements legacy UFS quota v1. Quota data is stored as fixed-size `struct dqblk` records in per-type quota files, indexed directly by user or group ID.

Key responsibilities:
- Enforce block and inode limits for quota v1.
- Update v1 usage counters and warning flags.
- Turn quota v1 files on and off.
- Read and write v1 dquot records from quota files.
- Convert between legacy `dqblk` state and fs-independent `quotaval` commands.
- Sync dirty dquots during mount sync and final release.

Important functions:
- `chkdq1`: Applies block usage deltas. Negative deltas reduce usage and clear warnings; positive deltas check hard/soft limits unless `FORCE`.
- `chkdqchg`: Checks block hard limits and soft-limit grace expiration, emitting user warnings.
- `chkiq1`: Applies inode usage deltas with the same negative/positive split.
- `chkiqchg`: Checks inode hard limits and soft-limit grace expiration.
- `quota1_umount`: Flushes vnodes and turns off all active v1 quota files.
- `quota1_handle_cmd_quotaon`: Opens the quota file, rejects WAPBL logging, marks the vnode system, saves credentials, initializes grace defaults, and attaches dquots to active writable vnodes.
- `quota1_handle_cmd_quotaoff`: Marks closing state, detaches dquots from all active vnodes, closes the quota file, frees credentials, and clears mount quota flags when appropriate.
- `quota1_handle_cmd_get`: Returns block or file quota values, using ID 0 as default/grace source for `QUOTA_DEFAULTID`.
- `quota1_handle_cmd_put`: Updates limits and grace periods, preserving current usage and recalculating expiration when crossing soft limits.
- `q1sync`: Walks mount vnodes and syncs modified dquots.
- `dq1get`: Reads a `dqblk` from the quota file; a missing record becomes a zeroed quota.
- `dq1sync`: Writes a dirty `dqblk` back to the quota file and clears `DQ_MOD`.

Important interactions:
- Uses common `dqget`, `dqrele`, `getinoquota`, `dqlock`, and `dqcv`.
- Mutates `ufsmount` fields `um_quotas`, `um_cred`, `umq1_btime`, `umq1_itime`, and `umq1_qflags`.
- V1 cannot be used with `-o log`/WAPBL journaling in this implementation.

Notable behavior and risks:
- Limit encoding maps `QUOTA_NOLIMIT` and values beyond 32-bit range to zero, matching v1’s 32-bit restriction.
- Quota-off waits for open/close transitions and detaches quota references from every vnode before closing the quota file.
- A large disabled `#if 0` block preserves older whole-`dqblk` and usage-setting routines but they are not active.
