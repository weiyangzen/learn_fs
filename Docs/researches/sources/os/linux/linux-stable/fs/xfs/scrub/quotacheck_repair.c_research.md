# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck_repair.c

This file commits live quotacheck observations back into dquots.

Main unit:
- `xqcheck_commit_dquot` allocates a transaction, locks and joins a dquot, checks for aborted scan, loads observed counters, adjusts `reserved` and `count` fields by deltas for inode/block/realtime resources, marks the shadow record repair-scanned, logs dirty dquots, adjusts timers for non-root dquots, and commits.
- If nothing changed, it cancels the transaction.

Quota type repair:
- `xqcheck_commit_dqtype` first iterates existing dquots and commits observations to them.
- It then walks shadow observations that were not repair-scanned, creating missing dquots with `xfs_qm_dqget(..., true, ...)` and committing counters.

CHKD flag handling:
- `xqcheck_chkd_flags` computes active quota checked flags.
- `xrep_quotacheck` clears active CHKD flags and commits before changing dquots. This ensures a crash will force mount-time quotacheck.
- After all counters are committed, it starts a new transaction, restores CHKD flags, and commits.

This repair path relies on `quotacheck.c` leaving a complete live dataset in `sc->buf`.
