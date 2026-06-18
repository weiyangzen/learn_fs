# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl.c

## Role
Provides the primary XFS file ioctl implementation and file attribute get/set operations. It is a major userspace boundary for bulk inode queries, filesystem geometry, extent maps, labels, reserve blocks, growfs, handles, scrub, health monitoring, media verification, exchange/commit range, EOF block freeing, and other XFS management operations.

## Main Structures and Entry Points
- `xfs_file_ioctl` dispatches native ioctls.
- `xfs_fileattr_get` and `xfs_fileattr_set` implement VFS fileattr operations for XFS flags, project IDs, and extent size hints.
- `xfs_ioc_fsbulkstat`, `xfs_ioc_bulkstat`, and `xfs_ioc_inumbers` adapt legacy and v5 inode bulk query APIs to `xfs_itable`.
- `xfs_ioc_fsgeometry`, `xfs_ioc_ag_geometry`, and `xfs_ioc_rtgroup_geometry` report filesystem, allocation group, and realtime group geometry.
- `xfs_ioc_getbmap` returns data/attr fork extent maps via `xfs_getbmap`.
- `xfs_ioc_swapext` validates two XFS file descriptors before invoking extent swap.
- `xfs_ioc_getlabel` and `xfs_ioc_setlabel` expose and update the filesystem label.

## Behavior
Legacy bulkstat/inumbers ioctls copy `xfs_fsop_bulkreq`, enforce `CAP_SYS_ADMIN`, validate count and output buffers, translate the historical `lastip` cursor semantics into internal `xfs_ibulk.startino`, call bulkstat/inumbers walkers, and copy back the updated cursor and output count. The v5 bulk request setup validates flags, reserved fields, special inode requests, AG-limited walks, large extent-count output, and metadata-directory visibility.

File attribute updates validate unsupported flags, project ID width, quota setup, DAX cache behavior, realtime flag transitions, extsize and cowextsize alignment, and v3 inode feature requirements. Updates run in inode-change transactions, adjust project quota ownership if needed, update on-disk diflags/diflags2 and VFS flags, clear setuid/setgid where required, record timestamps, and commit or release dquot references on failure.

The dispatcher consistently gates privileged administrative operations, checks shutdown/read-only state where relevant, uses `mnt_want_write_file` for mutating operations, performs explicit `copy_from_user`/`copy_to_user`, and delegates specialized functionality to XFS subsystems.

## Interactions
This file connects userspace ioctls to `xfs_itable`, `xfs_iwalk`, growfs, discard, quota, fsmap, scrub, health, reflink/exchange range, handle, realtime geometry, zoned allocation, and block garbage collection subsystems. It also shares formatters with `xfs_ioctl32.c` through declarations in `xfs_ioctl.h`.

## Invariants and Error Handling
- Many ioctls require `CAP_SYS_ADMIN`; mutating paths additionally require writable mounts/files.
- Bulk request reserved fields must be zero and unsupported flags are rejected.
- Metadata directory files are hidden from legacy bulkstat unless explicitly requested through v5 flags.
- Realtime flag changes are rejected if the inode already has file data or if DAX device compatibility is unsafe.
- Label changes update the primary superblock, backup superblocks, and invalidate relevant block-device caches.
- Removed allocation/free-space ioctls intentionally return `-ENOTTY` with a one-time warning.
