# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota_stub.c

Read completely: 71 lines.

Provides no-op quota symbols for kernels built without `QUOTA`.

Core behavior:
- `getinoquota()`, block/inode allocation/free accounting, `quotaoff()`, `qsync()`, quota initialization, and inode quota deletion all return success or do nothing.
- `ufs_quotactl()` returns `EOPNOTSUPP`.

Integration and risks:
- Keeps call sites unconditional while removing runtime quota behavior.
- Must stay signature-compatible with `quota.h` and `ufs_quota.c`.
