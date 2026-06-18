# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2_subr.c

Read completely: 130 lines.

Provides quota2 metadata construction, byte-swapping, and limit-check helpers shared by kernel and non-kernel quota2 tooling.

Functions:
- `lfsquota2_addfreeq2e()` turns the free space in a quota block into a linked free list of `quota2_entry` records, starting at `baseoff % bsize`.
- `lfsquota2_create_blk0()` initializes quota block 0: clears the block, writes magic/type/hash geometry, sets default block and file hard/soft limits to unlimited, sets default grace to seven days, and initializes the first free entries after the hash table.
- `lfsquota2_ulfs_rwq2v()` byte-swaps all fields in a `quota2_val`.
- `lfsquota2_ulfs_rwq2e()` byte-swaps block/file values and owner id in a `quota2_entry`.
- `lfsquota_check_limit()` evaluates `cur + change` against hard and soft limits and grace expiry, returning allow/deny status plus soft-limit-crossing flag.

Semantics:
- Hard-limit overflow denies immediately.
- Soft-limit overflow is allowed when newly crossed or still within grace; denied after grace expiration.
- Crossing from below to over the soft limit returns `QL_F_CROSS` so callers can initialize expiration time.

Risks and notes:
- `cur + change` is computed in unsigned arithmetic without explicit overflow guarding.
- `lfsquota2_ulfs_rwq2e()` does not copy/swap `q2e_next`; callers handling list pointers swap that field directly.
