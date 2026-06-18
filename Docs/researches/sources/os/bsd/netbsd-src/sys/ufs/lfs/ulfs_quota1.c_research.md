# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.c

Read completely: 868 lines.

Implements deprecated quota1 support for ULFS/LFS. Quota1 stores an array of fixed-size `struct dqblk` records in ordinary quota files, indexed directly by user or group id.

Accounting:
- `lfs_chkdq1()` updates block usage. Negative changes subtract and clear warnings. Positive changes first check every applicable dquot against hard/soft limits unless `FORCE` or quota-nolimit authorization applies, then applies usage increments if all checks pass.
- `lfs_chkiq1()` applies the same pattern to inode/file usage.
- `chkdqchg()` and `chkiqchg()` enforce hard limits, soft-limit grace expiry, initialize grace timers on crossing, and print warnings/errors to the owning user.

Mount/unmount:
- `lfsquota1_handle_cmd_quotaon()` opens a quota file, rejects non-regular files, serializes with quota open/close flags, marks the mount and vnode as quota/system state, stores the enabling credential, loads default grace times from id 0, and attaches dquots to currently writable vnodes.
- `lfsquota1_handle_cmd_quotaoff()` serializes closing, clears `ULFS_QUOTA`, detaches dquots from vnodes, flushes diagnostics, closes the quota vnode, releases stored credentials, and clears `MNT_QUOTA` when no quota files remain.
- `lfsquota1_umount()` flushes non-system vnodes and turns off each active quota type.

Quotactl handlers:
- `lfsquota1_handle_cmd_get()` reads a dquot, converts `dqblk` to `quotaval` pairs, and returns block or file quota values.
- `lfsquota1_handle_cmd_put()` updates block/file limits, grace values for default id or id 0, soft-limit timers, fake-limit status, warning flags, and marks the dquot modified.

I/O and sync:
- `lfs_q1sync()` scans mount vnodes and synchronizes modified dquots.
- `lfs_dq1get()` reads the quota file record at `id * sizeof(struct dqblk)` and treats a short empty read as zeroed quota data.
- `lfs_dq1sync()` writes the quota record back and clears `DQ_MOD`.

Risks and notes:
- Quota1 has 32-bit on-disk limits and maps unlimited to zero in the legacy format.
- The file contains disabled legacy `setquota1()`/`setuse()` code.
- Limit checks compare `>=` against encoded quota1 limits; helper conversion in `ulfs_quota1_subr.c` maps legacy inclusive/exclusive semantics for modern `quotaval`.
- Quota file operations intentionally avoid charging the quota file itself to prevent recursion/deadlock.
