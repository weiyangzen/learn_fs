# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.h

This header defines the shared in-core quota structures and function prototypes used by UFS quota v1, quota v2, and common quota dispatch code.

Key responsibilities:
- Include on-disk quota v1 and v2 definitions.
- Define `struct dquot`, the common cached quota object.
- Define the quota2 disk-location descriptor embedded in dquots.
- Document dquot locking ownership and lock order.
- Provide shorthand macros for v1 quota fields and v2 entry locations.
- Declare shared quota globals and all v1/v2 helper functions.

Important structures and macros:
- `struct dq2_desc`: Logical block number and block offset of a quota2 entry.
- `struct dquot`: Hash linkage, flags, type, reference count, ID, mount pointer, interlock, and union of v1 `dqblk` or v2 disk-location descriptor.
- `DQ_MOD`: Dquot has modified state needing sync.
- `DQ_FAKE`: Dquot carries no real limits, only usage.
- `DQ_WARN(ltype)`: Warning-state bit for a block/file limit class.
- `NODQUOT`: Null quota pointer sentinel.
- `dq_bhardlimit`, `dq_curblocks`, `dq_itime`, etc.: v1 field aliases.
- `dq2_lblkno`, `dq2_blkoff`: v2 location aliases.

Important interactions:
- `ufs_quota.c` owns global dquot cache lifecycle and uses this structure for both implementations.
- `ufs_quota1.c` uses the `dq_un.dq1_dqb` part for flat-file quota records.
- `ufs_quota2.c` uses the `dq2_desc` part to locate quota2 entries in on-disk hash lists.

Notable behavior:
- Lock order is explicitly documented as `dq_interlock -> dqlock` and `dq_interlock -> dqvp`.
- The header is the ABI boundary between generic UFS quota dispatch and implementation-specific quota v1/v2 code.
