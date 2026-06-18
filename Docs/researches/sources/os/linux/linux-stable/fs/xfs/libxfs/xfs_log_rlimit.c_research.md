# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_rlimit.c

## Role
`xfs_log_rlimit.c` calculates the maximum transaction reservation relevant to minimum log sizing and derives the minimum legal XFS log size for a filesystem configuration.

## Main Responsibilities
- Preserve historical minimum log size behavior for older feature sets, even when old reservation formulas overestimated requirements.
- Enable corrected minimum-log calculations only for sufficiently new feature combinations, specifically v5 filesystems with parent pointers.
- Compute the worst-case local attr set transaction space.
- Build alternate transaction reservation tables for minimum log size calculations.
- Choose the largest transaction reservation and convert it into minimum log blocks.

## Important Functions
- `xfs_want_minlogsize_fixes` checks the superblock directly for v5 plus parent-pointer incompat feature because this code can run before mount feature flags are fully established.
- `xfs_log_calc_max_attrsetm_res` estimates maximum logged local attr value space and conditionally fixes an older unit conversion overestimate.
- `xfs_log_calc_trans_resv_for_minlogblocks` either uses current reservation calculations or deliberately recreates historical rmap/reflink reservation behavior for compatibility.
- `xfs_log_get_max_trans_res` scans a temporary reservation table and returns the largest effective reservation, comparing attrset worst case separately.
- `xfs_log_calc_minimum_size` turns the largest reservation into filesystem blocks, accounting for log v2 stripe unit padding and the `XFS_MIN_LOG_FACTOR`.

## Data and Invariants
- Minimum log size cannot be reduced for older feature sets because newer mkfs output must remain mountable on older kernels.
- For striped logs, two log stripe units are considered per transaction reservation because both transaction data and commit records can need padding.
- The minimum size uses a factor of three so at least two maximally sized transactions can fit with headroom.

## Dependencies
This file depends on transaction reservation calculation, DA attr geometry, bmap btree reservation helpers, mount/superblock feature checks, and tracepoints.

## Research Notes
This file intentionally contains compatibility math. Some calculations are known historical overestimates, but preserving mount compatibility takes precedence unless the filesystem has a new enough feature gate.
