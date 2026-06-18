# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_notify_failure.c

## Purpose
Implements DAX device failure notification for XFS, translating failed byte ranges into filesystem blocks, reporting affected media, killing DAX users, invalidating page cache, and shutting down the filesystem when metadata or unrecoverable mappings are affected.

## Main API
Exports `xfs_dax_holder_operations` with `.notify_failure = xfs_dax_notify_failure`, used by the DAX holder mechanism.

## Data Device Handling
For data and realtime devices, failure ranges are clipped to the filesystem’s device extent, converted to data FSBs or realtime blocks, and mapped to AGs or realtime groups. The code requires rmapbt support to identify file owners. It queries rmap records in each affected group and calls `mf_dax_kill_procs` for incore DAX file mappings, invalidates cache during pre-remove, and reports data loss through `fserror_report_data_lost`.

## Log Device Handling
External log failures are translated to log daddrs and reported to health monitoring. Normal log corruption notifications shut down the filesystem as on-disk corruption. Pre-remove notifications avoid log-device access failure handling and allow forced unmount flow.

## Pre-Remove Behavior
For `MF_MEM_PRE_REMOVE`, the filesystem is frozen to prevent new mappings where possible, all affected mappings are processed, and the filesystem is force-shutdown for unmount. The thaw path also releases userspace freeze state because the device is being removed.

## Failure Handling
Non-inode rmap owners, attr fork mappings, bmbt blocks, inode lookup failures, rmap query errors, or metadata exposure request shutdown with `SHUTDOWN_CORRUPT_ONDISK` outside pre-remove. Out-of-filesystem ranges return `-ENXIO`; missing rmapbt returns `-EOPNOTSUPP`.
