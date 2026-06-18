# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck.c

## Role
Implements live quotacheck: recomputes quota counters from every inode and compares the results to incore dquots.

## Setup
- `xchk_setup_quotacheck` requires quotas to be enabled, enables quota fsgates, allocates `struct xqcheck`, and sets up filesystem scrub state.
- `xqcheck_setup_scan` creates sparse counter arrays for active quota types, initializes a transaction shadow-accounting hash, installs quota transaction hooks, and sets deferred cleanup.

## Live Update Hooks
- `xqcheck_mod_live_ino_dqtrx` records quota deltas made to already scanned inodes in per-transaction shadow state.
- `xqcheck_apply_live_dqtrx` applies those shadow deltas to the recomputed counters when the real quota code commits and frees transaction shadow state.
- Hook errors abort the iscan to force `INCOMPLETE`.

## Collection
- `xqcheck_collect_counts` walks all allocated inodes with an empty transaction.
- `xqcheck_collect_inode` skips metadata/quota inodes, locks data state, counts data and realtime blocks, then increments user/group/project shadow counters for the inode’s ids.
- Realtime inodes load data fork mappings so realtime blocks can be counted accurately.

## Comparison
- `xqcheck_compare_dquot` compares observed inode, data block, and realtime block counts to a dquot.
- `xqcheck_compare_dqtype` first checks quota `CHKD` flags, iterates known dquots, then checks observed dquots that were not in the quota file.
- Missing incore dquots for observed ids are corruption.

## Risk Points
- The apply hook must be removed after the mod hook to avoid leaking shadow transaction state.
- Partial scans cannot be used for repair.
- Comparison handles all active quota types independently.
