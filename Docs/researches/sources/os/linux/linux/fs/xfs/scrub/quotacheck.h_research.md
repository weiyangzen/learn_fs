# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck.h

## Role
Defines live quotacheck data structures shared by scrub and repair.

## Structures
- `struct xqcheck_dquot` holds recomputed block, inode, and realtime block counts plus state flags.
- `struct xqcheck` holds scrub context, per-type sparse counter arrays, mutex, iscan, quota hooks, and transaction shadow-accounting hash table.

## Flags
- `XQCHECK_DQUOT_WRITTEN` marks initialized counter records.
- `XQCHECK_DQUOT_COMPARE_SCANNED` marks records compared by scrub.
- `XQCHECK_DQUOT_REPAIR_SCANNED` marks records repaired.

## Helper
- `xqcheck_counters_for` returns the appropriate sparse counter array for a quota type.
