# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/quota.h

Read completely: 149 lines.

Defines UFS quota constants, quotactl commands, on-disk quota record format, flags, and kernel quota APIs.

Core definitions:
- Supports two quota types: user and group, with default one-week soft-limit grace times.
- Defines quota command encoding with `QCMD()`, including quota on/off, get, set, set-use, and sync.
- `struct dqblk` is the quota-file record: hard/soft block limits, current blocks, hard/soft inode limits, current inodes, and block/inode grace-expiration times.
- Kernel flags let callers skip uid/gid accounting or force changes without limit checks.
- Declares quota accounting, quota deletion, quota file control, sync, and initialization functions; when quota is disabled, matching stubs are provided elsewhere.

Integration and risks:
- The `dqblk` timestamps are 32-bit and explicitly carry a 2038 concern.
- `MAXQUOTAS` is baked into inode and mount arrays.
- Accounting callers depend on matching allocation/free semantics during ownership changes and rollback.
