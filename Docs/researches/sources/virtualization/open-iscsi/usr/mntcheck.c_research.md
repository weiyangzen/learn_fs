# File Research: sources/virtualization/open-iscsi/usr/mntcheck.c

Purpose: Checks whether block devices attached to an iSCSI session are currently in use by mounted filesystems, swap, partitions, or stacked block-device holders.

Key entry point:
- `session_in_use(int sid)` initializes libmount tables, resolves the iSCSI host number for the SID, iterates session devices, counts users, cleans up libmount state, and returns the count.

Implementation notes:
- `libmount_init()` creates mount and swap tables, attaches a cache, parses current mtab and swaps, and returns `-ENOMEM` on allocation failure.
- `blockdev_check_mnts()` reads `DEVNAME` from a sysfs `uevent`, builds `/dev/<name>`, and searches both mount and swap tables for that source.
- `blockdev_get_partitions()` scans child sysfs directories and recurses into those whose `uevent` `DEVTYPE` is `partition`.
- `blockdev_get_holders()` scans a device's `holders` directory, resolves holder symlinks with `realpath()`, and recurses into stacked devices such as dm/md layers.
- `count_device_users()` combines direct mount/swap checks, partition checks, and holder checks.
- `device_in_use()` maps a host/target/lun to a block device name using `iscsi_sysfs_get_blockdev_from_lun()` and checks `/sys/class/block/<dev>`.

Dependencies and interactions:
- Uses libmount for mounted filesystem and swap lookups.
- Uses iSCSI sysfs helpers for SID-to-host and LUN-to-block-device traversal.
- Reads generic sysfs `uevent` fields via `sysfs_get_uevent_devtype()` and `sysfs_get_uevent_devname()`.

Filesystem/storage relevance:
- This file protects session logout or shutdown flows from disconnecting iSCSI-backed block devices still in use by filesystems, swap, partitions, or upper-layer block mappings.
