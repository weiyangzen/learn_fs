# File Research: sources/os/linux/linux-stable/fs/sysfs/symlink.c

Purpose: Implements sysfs symlink creation, deletion, removal, and rename helpers.

Key responsibilities:
- Creates symlinks from a parent kernfs node or kobject directory to a target kobject.
- Provides warning and no-warning creation variants.
- Supports root-level symlink creation when the source kobject is NULL.
- Deletes symlinks with namespace awareness through `sysfs_delete_link()`.
- Removes symlinks by name.
- Renames symlinks while validating that the old entry is a link to the expected target.

Important interactions:
- Uses `sysfs_symlink_target_lock` to safely inspect `target_kobj->sd`.
- Uses kernfs link, lookup, remove, and rename operations.
- Exports public sysfs symlink APIs to GPL modules.

Notable invariants and risks:
- Target kobjects may disappear independently of the link creator; the shared lock prevents dereferencing a freed `sd` pointer.
- Namespace-aware deletion needs target information; plain removal does not validate target namespace.
