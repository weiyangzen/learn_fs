# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_rlimit.c

## Role

This file calculates minimum valid XFS log sizes from transaction reservation requirements. It preserves compatibility with older kernels by intentionally retaining historic overestimates for older feature sets, while allowing corrected calculations for newer parent-pointer filesystems.

## Compatibility Gate

`xfs_want_minlogsize_fixes` enables corrected minimum-log-size calculations only for v5 filesystems with the parent pointer incompat feature. This avoids formatting filesystems that older kernels would reject because the log became smaller than their historical minimum calculation expected.

## Attribute Reservation Calculation

`xfs_log_calc_max_attrsetm_res` estimates the largest local attr-set reservation. It computes the maximum local attr value size, directory/attr tree block needs, and extent-add reservation. For parent-pointer-era filesystems it corrects a previous unit conversion error by converting bytes to filesystem blocks before feeding the next-extent reservation macro.

## Alternate Reservation Table

`xfs_log_calc_trans_resv_for_minlogblocks` builds a transaction reservation table specifically for minimum log size calculations.

For old feature sets it preserves older behavior:

- temporarily forces old reflink+rmap maximum rmapbt level
- recomputes reservations
- copies dynamic atomic ioend reservation
- restores older write, truncate, and dquot-allocation log counts for rmap/reflink cases
- recomputes older write/truncate/dquot allocation log reservations that predate deferred refcount update log items

For new parent-pointer feature sets it uses current `xfs_trans_resv_calc` output plus dynamic atomic ioend reservation.

## Minimum Log Size

`xfs_log_get_max_trans_res` walks the alternate reservation table, finds the largest reservation considering log count, compares against maximum attr-set reservation, and returns the maximum transaction reservation.

`xfs_log_calc_minimum_size` converts that maximum transaction reservation to filesystem blocks. It accounts for log v2 stripe unit padding, requires enough room for two maximally sized transactions and padding, multiplies by `XFS_MIN_LOG_FACTOR`, and returns the rounded filesystem block count.

## Dependencies

This file depends on mount geometry, superblock feature checks, transaction reservation calculators, attr geometry, bmap/da reservation macros, and tracepoints.

## Research Notes

The file is deliberately conservative because minimum log size is a format interoperability boundary. The parent-pointer feature is used as a forward-compatibility marker for when smaller corrected minimum logs are safe.
