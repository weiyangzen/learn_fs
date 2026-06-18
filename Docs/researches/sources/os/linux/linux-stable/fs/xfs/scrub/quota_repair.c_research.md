# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota_repair.c

This file repairs quota file metadata and dquot fields.

Repair goals:
- Fix dquot verifier failures.
- Cap nonsensical soft limits and resource counters.
- Repair quota file data fork mappings.
- Schedule quotacheck if usage counters had to be clamped to uncertain values.

Backing mapping repair:
- `xrep_quota_item_bmap` computes the expected quota-file offset and ensures a real written mapping backs the dquot.
- Holes or delalloc/unreal mappings are fixed by `xrep_quota_item_fill_bmap_hole`, which allocates quota-file space, initializes a dquot cluster, and rolls the transaction.
- Incorrect cached `q_blkno` values are updated.

Per-dquot repair:
- `xrep_quota_item` locks the quota inode and dquot, repairs backing mapping, clamps soft limits to hard limits, clamps impossible physical counts on non-reflink filesystems, adjusts reserved counters by the delta, fixes timers through normal dquot adjustment, marks dirty, logs the dquot, and rolls.
- If counters are clamped, `need_quotacheck` is set because exact values require a full scan.

Disk block repair:
- `xrep_quota_block` reads quota blocks through verifiers. On verifier failure, it rereads without ops and rebuilds every dquot record in the chunk.
- It restores magic/version/type/id, bigtime flag, UUID, checksum, buffer type, and missing timers needed to pass verifiers.

Quota data fork repair:
- `xrep_quota_data_fork` repairs generic metadata inode forks, rejects delalloc, truncates mappings beyond maximum dquot id, converts unwritten extents to written extents, clears reflink state after truncation, and fixes every dquot block.

Main flow:
- `xrep_quota` ensures exclusive quota inode lock, repairs fork and disk blocks, finishes deferred work, rolls and unlocks the quota inode, repairs live dquot problems, forces quotacheck if needed, and commits.
