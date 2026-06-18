# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.h

Read completely: 129 lines.

Defines the quota2 on-disk metadata format and quota limit status codes.

Format:
- `struct quota2_val` stores hard limit, soft limit, current usage, grace expiration time, and grace duration.
- `N_QL` is 2, with `QL_BLOCK` and `QL_FILE` for block and file/inode quota objects.
- `struct quota2_entry` stores block/file values, next-entry offset for hash/free lists, and owner id.
- `struct quota2_header` stores magic, quota type, hash shift/size, default quota entry, free-list head, and a variable-length hash table.
- `Q2_HEAD_MAGIC` validates quota2 metadata.
- `FS_Q2_DO_TYPE(type)` maps quota type to the LFS superblock quota flags.

Offset helpers:
- `off2qindex()` and `qindex2off()` translate between quota-entry byte offsets and entry indices after the variable-size header area.

Subroutine prototypes:
- `lfsquota2_addfreeq2e()` initializes free-list entries.
- `lfsquota2_create_blk0()` creates the initial quota header block.
- `lfsquota2_ulfs_rwq2v()` and `lfsquota2_ulfs_rwq2e()` byte-swap quota values and entries.

Limit status:
- `QL_S_ALLOW_OK`, `QL_S_ALLOW_SOFT`, `QL_S_DENY_GRACE`, and `QL_S_DENY_HARD` classify quota checks.
- `QL_F_CROSS` reports crossing a soft limit.
- `QL_STATUS()` and `QL_FLAGS()` split status bits.
- `lfsquota_check_limit()` is the shared checker.

Risks and notes:
- The header assumes filesystem-independent quota object constants match quota2 indices; implementation uses `CTASSERT()` to enforce this.
- The variable-length header means block 0 layout depends on configured hash size.
