# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.c

This file implements live quota counter scrub by independently rebuilding quota usage from all inodes and comparing that to live dquots.

Setup:
- `xchk_setup_quotacheck` requires quotas to be enabled, enables quota fsgates, allocates `struct xqcheck`, and sets up filesystem scrub.
- `xqcheck_setup_scan` creates sparse counter arrays for active quota types, starts an inode scan, initializes a transaction-to-delta rhashtable, and installs quota transaction hooks.

Collection:
- `xqcheck_collect_counts` cancels the normal scrub transaction, uses an empty transaction, scans all allocated inodes, and later restores normal filesystem scrub setup.
- `xqcheck_collect_inode` skips metadir and quota inodes, locks regular/realtime files appropriately, counts data and realtime blocks, and updates user/group/project shadow counters.
- Realtime files load data fork extents so realtime block usage can be separated.

Live quota update tracking:
- `xqcheck_mod_live_ino_dqtrx` tracks per-transaction dquot deltas for inodes that were already scanned.
- `xqcheck_apply_live_dqtrx` applies those deltas to the shadow counters when the real quota code commits them.
- Shadow delta state is keyed by transaction id in `shadow_dquot_acct`.
- Hook failures abort the iscan so scrub reports incomplete instead of false corruption.

Comparison:
- `xqcheck_compare_dquot` compares observed inode/block/realtime block counts with a locked live dquot, then marks the shadow record scanned.
- `xqcheck_compare_dqtype` first treats missing quota CHKD flags as corruption, then walks real dquots and shadow observations.
- `xqcheck_walk_observations` catches observed ids that have no corresponding dquot.

Teardown:
- `xqcheck_teardown_scan` aborts the iscan, removes hooks in safe order, destroys the rhashtable and arrays, and clears state.
- The cleanup is deferred so successful scrub data remains available to `quotacheck_repair.c`.

Main scrub:
- `xchk_quotacheck` sets up live tracking, collects counts, fails fast on incomplete datasets, compares active quota types, and performs a final aborted-scan check.
