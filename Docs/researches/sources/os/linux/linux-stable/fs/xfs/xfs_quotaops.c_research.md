# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_quotaops.c

## Purpose
Adapts XFS quota manager syscalls to the VFS `quotactl_ops` interface.

## Main APIs
Defines `xfs_quotactl_operations` with handlers for quota state reporting, quota timer setting, quota enable/disable, quota file removal, get/set dquot blocks, and get-next dquot scanning.

## Key Behavior
`xfs_fs_get_quota_state` reports in-core dquot count, accounting/enforcement flags, quota inode numbers, quota file block/extent counts, and default grace periods for user/group/project quota types. `xfs_qm_fill_state` loads each quota inode temporarily to fill per-type state.

VFS quota type ids are translated to XFS dquot types by `xfs_quota_type`. Userspace quota flags are translated to XFS accounting/enforcement bits by `xfs_quota_flags`.

`xfs_fs_set_info` supports timer fields only and implements them by setting id-0 quota limits through `xfs_qm_scall_setqlim`. Get/set dquot handlers translate `kqid` ids through user namespaces and dispatch to quota manager get/set helpers.

Quota file removal is allowed only when quotas are off and maps user/group/project flags to quota metadata file truncation.

## Dependencies
Uses VFS quotactl structs, superblock readonly checks, XFS mount quota flags, quota manager syscall helpers, quota inode loading, and current/init user namespace id conversion.

## Failure Handling
Read-only filesystems return `-EROFS`; disabled quota state returns `-ENOSYS`; invalid flag or field masks return `-EINVAL`. Quota file removal refuses to run while quotas are active.
