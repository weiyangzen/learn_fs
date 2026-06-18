# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.h

Read completely: 146 lines.

Defines the common in-core quota object and prototypes shared by quota1, quota2, and the generic quota dispatcher.

Core structures:
- `struct dq2_desc` records the quota2 metadata location of an on-disk quota entry as logical block number plus block offset.
- `struct dquot` is the cached per-id quota object. It contains hash linkage, flags, type, refcount, id, mount pointer, per-dquot mutex, and a union storing either quota1 usage/limits (`struct dqblk`) or quota2 location (`struct dq2_desc`).

Flags and aliases:
- `DQ_MOD` marks dirty quota1 dquots.
- `DQ_FAKE` marks quota1 entries with no real limits.
- `DQ_WARN(ltype)` records that a warning has already been issued for block/file quota type.
- Shorthand macros expose quota1 fields (`dq_bhardlimit`, `dq_curblocks`, etc.) and quota2 location fields (`dq2_lblkno`, `dq2_blkoff`).
- `NODQUOT` is null.

Exported functions:
- Generic dquot cache and inode functions: `lfs_getinoquota()`, `lfs_dqget()`, `lfs_dqref()`, `lfs_dqrele()`, and diagnostic `lfs_dqflush()`.
- Quota1 accounting, sync, dquot I/O, and command handlers.
- Quota2 accounting, get/put/delete, cursor command handlers, sync hooks, and dquot lookup hooks.

Role:
- This header is the bridge between VFS/inode quota accounting and the two backing quota formats.

Risks and notes:
- The documented lock ordering is central to avoiding deadlocks: `dq_interlock` must precede global `lfs_dqlock` or quota vnode operations.
- The same `struct dquot` union has very different meanings in quota1 and quota2, so callers must dispatch by filesystem quota mode.
