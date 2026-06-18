# File Research: sources/os/linux/linux/fs/xfs/xfs_notify_failure.c

## Purpose

`xfs_notify_failure.c` implements DAX media failure notification handling for XFS. It translates DAX-device failure ranges into filesystem block ranges, reports media health events, identifies affected file mappings through reverse-mapping btrees, kills affected DAX mappings/processes where appropriate, invalidates pages for pre-removal, and shuts down the filesystem when metadata or log corruption is implied.

## Main Data Structure

`struct xfs_failure_info` carries:

- group-relative start block,
- block count,
- memory failure flags,
- `want_shutdown` flag set when non-file metadata or lookup failures imply unsafe state.

## Main Functions

- `xfs_failure_pgoff`: computes file page offset for the overlap between a reverse map record and the failed range.
- `xfs_failure_pgcnt`: computes affected page count for the overlap.
- `xfs_dax_failure_fn`: rmap query callback that handles each affected extent.
- `xfs_dax_notify_failure_freeze`: freezes the filesystem under kernel holder before pre-remove handling.
- `xfs_dax_notify_failure_thaw`: thaws kernel and userspace holders after pre-remove handling.
- `xfs_dax_translate_range`: maps DAX failure offset/length to filesystem device daddr and basic-block length.
- `xfs_dax_notify_logdev_failure`: handles failure on an external log device.
- `xfs_dax_notify_dev_failure`: handles data or realtime device failures by querying rmap metadata.
- `xfs_dax_notify_failure`: dispatches failure notification based on which XFS buftarg owns the DAX device.

## Behavior

For file-owned rmap records, the callback tries to get an incore inode. If the inode is DAX-backed, it calls `mf_dax_kill_procs` for the affected file page range. For pre-remove notifications it invalidates affected page cache ranges. It always reports data loss through `fserror_report_data_lost`.

For metadata, attr fork, bmbt block, missing inode, or other unsafe cases, the code requests filesystem shutdown unless this is a pre-remove path where forced unmount is expected.

## Device Handling

- Whole-device notification is represented by `offset == 0 && len == U64_MAX`.
- Out-of-filesystem ranges return `-ENXIO`.
- Log device failure reports health and shuts down as corrupt on-disk state unless pre-remove.
- Data/realtime failure requires rmapbt; otherwise it returns `-EOPNOTSUPP`.

## Pre-Remove Handling

When `MF_MEM_PRE_REMOVE` is set, XFS logs that the device is about to be removed, attempts to freeze the filesystem to prevent new mappings, scans affected mappings, then force-shuts down with `SHUTDOWN_FORCE_UMOUNT` and thaws holders.

## Exported Interface

The file exports `xfs_dax_holder_operations` with `.notify_failure = xfs_dax_notify_failure`.
