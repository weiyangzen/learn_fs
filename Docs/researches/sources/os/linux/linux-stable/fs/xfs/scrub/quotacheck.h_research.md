# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quotacheck.h

This header defines live quotacheck shadow counter state.

`struct xqcheck_dquot` stores observed:
- block count,
- inode count,
- realtime block count,
- flags.

Flags:
- `XQCHECK_DQUOT_WRITTEN`: sparse record initialized.
- `XQCHECK_DQUOT_COMPARE_SCANNED`: compared during scrub.
- `XQCHECK_DQUOT_REPAIR_SCANNED`: committed during repair.

`struct xqcheck` stores:
- scrub context,
- sparse arrays for user/group/project counters,
- mutex protecting observations,
- inode scan state,
- quota transaction hooks,
- rhashtable for shadow dquot accounting by transaction.

`xqcheck_counters_for` maps dquot type to the correct sparse counter array and asserts on invalid types.

This header is shared by live quotacheck scrub and repair.
