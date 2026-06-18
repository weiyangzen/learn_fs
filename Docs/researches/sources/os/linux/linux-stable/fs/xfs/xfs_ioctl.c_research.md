# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.c

This file is the primary native ioctl implementation for XFS. It bridges userspace XFS-specific ioctl ABI requests to filesystem internals for bulk inode queries, geometry, file attributes, extent maps, handles, growfs, labels, reserved blocks, scrub, health, media verification, eof block reclamation, and range exchange/commit operations.

Major areas:
- Legacy bulkstat and inumbers:
  - `xfs_ioc_fsbulkstat` supports `XFS_IOC_FSBULKSTAT_SINGLE`, `XFS_IOC_FSBULKSTAT`, and `XFS_IOC_FSINUMBERS`.
  - `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` convert current internal records to legacy ABI structures.
- v5 bulkstat and inumbers:
  - `xfs_bulk_ireq_setup` validates `xfs_bulk_ireq`, handles special root inode lookup, AG-scoped iteration, metadata-directory exposure, and 64-bit extent-count flags.
  - `xfs_ioc_bulkstat` and `xfs_ioc_inumbers` drive `xfs_bulkstat` / `xfs_inumbers` and write back updated cursors.
- Geometry:
  - `xfs_ioc_fsgeometry` emits v1/v4/v5 filesystem geometry.
  - `xfs_ioc_ag_geometry` reports per-AG geometry.
  - `xfs_ioc_rtgroup_geometry` reports realtime group geometry and, for zoned filesystems, current write pointer state through `xfs_rtgroup_report_write_pointer`.
- File attributes:
  - `xfs_fileattr_get` and `xfs_ioc_fsgetxattra` expose data-fork or attr-fork `file_kattr`.
  - `xfs_fileattr_set` validates and commits xflags, project IDs, extent-size hints, CoW extent-size hints, DAX state preparation, quota accounting, and project quota transfer.
- Extent maps and swapping:
  - `xfs_ioc_getbmap` handles `GETBMAP`, `GETBMAPA`, and `GETBMAPX`.
  - `xfs_ioc_swapext` validates file descriptors, modes, XFS file operations, mount identity, and swapfile status before calling `xfs_swap_extents`.
- Label and reserved blocks:
  - `xfs_ioc_getlabel` and `xfs_ioc_setlabel` read/write the superblock label, sync the primary superblock, update secondary superblocks, and invalidate block-device page cache.
  - `xfs_ioctl_getset_resblocks` gets or sets global reserved block pool state.
- Main dispatcher:
  - `xfs_file_ioctl` routes native ioctl commands, including `FITRIM`, labels, DIO alignment info, bulkstat, geometry, parent pointers, fsmap, scrub, handle operations, attr-by-handle operations, growfs, goingdown, error injection, eof block freeing, exchange/commit range, health monitor, and media verify.

Permission and safety patterns:
- Administrative ioctls generally require `CAP_SYS_ADMIN`.
- Mutating ioctls use `mnt_want_write_file` / `mnt_drop_write_file`.
- Shutdown and readonly checks are used where needed.
- Userspace structures are copied with `copy_from_user`, `copy_to_user`, `get_user`, and `put_user`, with reserved-field validation for newer ABIs.
- File attribute changes integrate with quota allocation and transaction logging before committing.

Integration points:
- Calls into `xfs_itable.c` for bulk inode enumeration.
- Calls into `xfs_iwalk.c` indirectly through bulkstat/inumbers.
- Uses growfs, trim, quota, health, scrub, handle, fsmap, reflink, realtime, zone, and media verification subsystems.

Risk notes:
- This is a broad ABI dispatcher, so compatibility and strict validation are central.
- File attribute updates are transaction-heavy and interact with DAX, realtime placement, quotas, and inode flags.
- Label setting intentionally performs extra synchronous writes and cache invalidation to satisfy userspace discovery tools.
