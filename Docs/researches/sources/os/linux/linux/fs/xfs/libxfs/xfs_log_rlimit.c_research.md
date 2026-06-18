# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_rlimit.c

This file computes maximum transaction reservations and minimum valid log size for a filesystem configuration, while preserving historical compatibility behavior.

Major responsibilities:
- Decide whether corrected minimum-log-size calculations are allowed through `xfs_want_minlogsize_fixes`.
- Calculate worst-case local attr set/remove reservation for minimum-log sizing.
- Build an alternate transaction reservation table for minimum-log calculations.
- Preserve older overestimates for filesystems lacking newer parent-pointer feature bits.
- Determine the largest reservation via `xfs_log_get_max_trans_res`.
- Compute minimum log size in filesystem blocks through `xfs_log_calc_minimum_size`.

Important compatibility behavior:
- Historical large-extent-count and reflink/rmap reservation bugs overestimated minimum log sizes.
- The code avoids reducing minimum log size for older feature sets so filesystems made by newer mkfs remain mountable by older kernels.
- Corrected calculations are only enabled for sufficiently new feature sets, currently gated by parent pointers on v5 filesystems.
- For old rmap+reflink behavior, `m_rmap_maxlevels` is temporarily forced to `XFS_OLD_REFLINK_RMAP_MAXLEVELS`.

Minimum log sizing rules:
- A single transaction must fit within a safe fraction of the log.
- The log must accommodate two maximally sized transactions.
- If a log stripe unit exists, padding for transaction data and commit record is included.
- Final result is converted from basic blocks to filesystem blocks.

Risk notes:
- This code affects mkfs and mount accept/reject decisions.
- Reducing historical minimums prematurely would create cross-version mount incompatibility.
- Reservation calculations depend on transaction reservation helpers and feature predicates.
