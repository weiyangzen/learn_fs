# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dqiterate.c

## Role

Quota dquot iterator for scrub/repair. It walks both on-disk quota file mappings and incore dquot caches so scrub can visit all relevant dquots, including incore dquots whose backing mappings may need repair.

## Key Functions

- `xchk_dqiter_init()` initializes the iterator for a scrub context and quota type.
- `xchk_dquot_iter_revalidate_bmap()` ensures the cached quota file mapping covers the current dquot id and matches the fork sequence.
- `xchk_dquot_iter_advance_bmap()` skips quota file holes to the next real mapped dquot chunk.
- `xchk_dquot_iter_advance_incore()` finds the next cached dquot id in the quota radix tree.
- `xchk_dquot_iter()` chooses the next dquot id from ondisk or incore sources, gets the dquot with `xfs_qm_dqget`, advances the cursor, and returns iteration status.

## Research Notes

The iterator accounts for quota repair scenarios where incore dquots can outlive or precede repaired quota file mappings. It locks the quota inode data fork only while validating bmap state and uses the quota tree lock for incore radix-tree lookup.
