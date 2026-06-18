# File Research: sources/os/linux/linux-stable/fs/sysfs/group.c

Purpose: Provides sysfs attribute-group creation, update, removal, merge/unmerge, symlink-in-group, compatibility link, and ownership-change operations.

Key responsibilities:
- Creates regular and binary attributes from `struct attribute_group`.
- Applies `is_visible`, `is_visible_const`, `is_bin_visible`, and `bin_size` callbacks.
- Handles named subdirectory groups and unnamed groups on the kobject directory.
- Rolls back partial group creation on errors.
- Updates group visibility by removing and re-adding files as needed.
- Removes groups and group lists.
- Merges extra files into existing named groups and unmerges them later.
- Adds/removes symlinks inside groups.
- Implements `compat_only_sysfs_link_entry_to_kobj()` for compatibility symlinks to target groups or attributes.
- Changes ownership of groups and their visible attributes.

Important interactions:
- Uses helpers from `file.c` for file creation and ownership.
- Uses `sysfs_symlink_target_lock` when linking to target kobjects not owned by the caller.
- Uses kernfs for directories, files, removal, lookup, and attribute mutation.

Notable invariants and risks:
- Attribute permissions are masked to allowed sysfs bits and warn on invalid modes.
- Group update semantics can remove existing entries before recreation; callers must tolerate transient changes.
- Visibility callbacks influence both creation and later ownership traversal.
