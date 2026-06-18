# File Research: sources/os/linux/linux/fs/sysfs/group.c

Purpose: Batch creation, update, merge, removal, symlink insertion, and ownership changes for sysfs attribute groups.

Key APIs:
- `sysfs_create_group`, `sysfs_create_groups`
- `sysfs_update_group`, `sysfs_update_groups`
- `sysfs_remove_group`, `sysfs_remove_groups`
- `sysfs_merge_group`, `sysfs_unmerge_group`
- `sysfs_add_link_to_group`, `sysfs_remove_link_from_group`
- `compat_only_sysfs_link_entry_to_kobj`
- `sysfs_group_change_owner`, `sysfs_groups_change_owner`

Implementation notes:
- Visibility callbacks `is_visible`, `is_visible_const`, and `is_bin_visible` determine whether files/groups are created and with which mode.
- `SYSFS_GROUP_INVISIBLE` can suppress an entire named group via first-visible check.
- Update mode removes existing files before re-adding currently visible ones.
- Creation unwinds previously created files/groups on error.
- Merge/unmerge operates on pre-existing named groups and fails if the group is absent.

Concurrency and correctness:
- Symlink-to-target compatibility helper uses `sysfs_symlink_target_lock` to safely reference target `kobj->sd`.
- Ownership change walks visible attributes and bin_attrs, applying kernfs `ATTR_UID | ATTR_GID`.
- Missing visible files during ownership change return `-ENOENT`.
