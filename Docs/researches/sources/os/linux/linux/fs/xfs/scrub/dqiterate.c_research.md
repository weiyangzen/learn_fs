# File Research: sources/os/linux/linux/fs/xfs/scrub/dqiterate.c

## Role
Implements a quota dquot iterator for scrub code that walks both ondisk quota file mappings and incore cached dquots.

## Main Interfaces
- `xchk_dqiter_init`: initializes cursor state, strips quota type to record mask, stores the quota inode, and starts at id zero.
- `xchk_dquot_iter`: returns the next dquot, or zero at end, using both quota file block mappings and incore radix tree state.

## Mapping Logic
- `xchk_dquot_iter_revalidate_bmap` refreshes the cached quota file bmap when the cursor id is outside the cached mapping or the fork sequence changed.
- `xchk_dquot_iter_advance_bmap` skips sparse quota file holes by reading subsequent mappings until it finds a real extent or reaches the maximum dquot id.
- `xchk_dquot_iter_advance_incore` checks the quota radix tree for the next cached dquot id, accounting for cases where repair removed an ondisk mapping but an incore dquot still must be handled.

## Iteration Semantics
- Locks the quota inode data map while revalidating or advancing bmaps.
- Chooses the smaller of the next ondisk-backed id and next incore id.
- Calls `xfs_qm_dqget` to return a referenced dquot and advances `cursor->id` past that dquot.

## Invariants and Edge Cases
- Ends when cursor id exceeds `XFS_DQ_ID_MAX` or no ondisk/incore ids remain.
- Treats impossible missing or forward mappings from `xfs_bmapi_read` as corruption.
- Caller must not hold the quota file ILOCK and must release returned dquots according to quota manager rules.
