# File Research: sources/os/linux/linux/fs/xfs/scrub/quotacheck_repair.c

## Role
Repairs quota counters using live quotacheck observations left active from scrub.

## Dquot Commit
- `xqcheck_commit_dquot` allocates a transaction, locks and joins the dquot, loads observed counters, adjusts reserved/count fields by deltas, updates timers, logs the dquot, and commits if dirty.
- Records are marked `XQCHECK_DQUOT_REPAIR_SCANNED`.

## Quota-Type Commit
- `xqcheck_commit_dqtype` first repairs every dquot known to the quota file.
- A second pass walks observed sparse records and creates missing dquots with `xfs_qm_dqget(..., true)` before committing counters.

## CHKD Flags
- `xqcheck_chkd_flags` computes active quota check flags.
- `xrep_quotacheck` clears CHKD flags before repair so a crash forces mount-time quotacheck, then restores them after all counters are committed.

## Risk Points
- Repair aborts if the original live scan was aborted.
- Creating missing dquots may allocate quota blocks in separate transactions.
- Crash safety relies on clearing CHKD before counter rewrites.
