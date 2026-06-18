# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota.c

This file scrubs individual quota files and dquot records for user, group, or project quotas.

Setup:
- `xchk_quota_to_dqtype` maps scrub type to XFS dquot type.
- `xchk_setup_quota` requires quotas to be enabled, verifies the requested quota type is active, optionally enables drain gates, sets up filesystem scrub, installs the quota inode as the live inode, and locks it exclusively.

Quota inode fork checks:
- `xchk_quota_data_fork` first invokes generic metadata inode fork scrub.
- It then scans data fork extents to reject delalloc/unwritten extents and mappings beyond the maximum dquot id offset.

Per-dquot checks:
- `xchk_quota_item_bmap` validates that the dquot’s cached file offset and disk block match a real written quota file mapping.
- `xchk_quota_item_timer` checks that timers are present only when soft/hard limits are exceeded.
- `xchk_quota_item` validates monotonic dquot ids, backing mapping, limit ordering, suspicious limits larger than filesystem resources, resource counts, hard-limit overages, and timers.

Important policy:
- On reflink filesystems, block usage can exceed physical block counts because shared blocks complicate accounting; this is warning-level unless limits are invalid.
- Non-reflink over-physical usage is corruption.
- Root dquot limit overage/timer checks are skipped where appropriate.

Main scrub:
- `xchk_quota` checks the quota inode fork, unlocks the quota inode, iterates all dquots with the dquot iterator API, and checks each dquot.
- Corruption during item iteration can short-circuit with `-ECANCELED`, then return success with scrub flags set.
