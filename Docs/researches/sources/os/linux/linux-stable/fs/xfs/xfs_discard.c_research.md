# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_discard.c

## Purpose
Implements online discard and FITRIM support for XFS data and realtime devices, using busy extent records to prevent allocation while discard I/O is in flight.

## Main APIs
- `xfs_discard_extents` issues discard bios for a list of busy extents and clears them asynchronously on completion.
- `xfs_ioc_trim` handles the user-facing FITRIM ioctl range validation and dispatches trimming for data and realtime devices.

## Data Device Trim
The data-device path repeatedly locks AGF state, searches free-space btrees in bounded batches, marks eligible free extents busy-under-discard, drops AGF locks, and issues discard asynchronously. Cursor state supports by-length scans for full AGs and by-block-number scans for partial ranges.

## Realtime Trim
With `CONFIG_XFS_RT`, realtime trimming supports both legacy non-rtgroup and rtgroup modes. Legacy realtime device discard uses synchronous `submit_bio_wait` because it does not use the normal busy extent machinery. Rtgroup mode queues busy extents and reuses `xfs_discard_extents` for async completion.

## FITRIM Semantics
`xfs_ioc_trim` requires `CAP_SYS_ADMIN`, discard-capable data or realtime devices, and no norecovery mount. User byte ranges are converted to daddrs; the realtime device appears after the data device in FITRIM address space. `minlen` is raised to device discard granularity.

## Failure and Stop Conditions
Loops stop for fatal signals or freezing. Corrupt btree records mark the btree sick and return corruption errors. Per-AG/rtgroup errors are remembered and the last error is returned after attempting remaining ranges.
