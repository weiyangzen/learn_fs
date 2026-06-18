# File Research: sources/os/linux/linux-stable/fs/sysfs/dir.c

Purpose: Implements sysfs directory creation, removal, rename, movement, and empty mount-point helpers on top of kernfs.

Key responsibilities:
- Defines `sysfs_symlink_target_lock`, shared with symlink and compatibility link paths to protect `kobj->sd` target access.
- `sysfs_create_dir_ns()` creates a kobject directory under its parent or sysfs root, applying kobject ownership and optional namespace tag.
- `sysfs_remove_dir()` clears `kobj->sd` under the symlink target lock and removes the kernfs directory.
- Provides rename and move helpers with namespace support.
- Implements exported empty mount-point helpers.

Important interactions:
- Uses kernfs directory APIs and `kobject_get_ownership()`.
- Duplicate creation emits a sysfs warning and stack dump via `sysfs_warn_dup()`.

Notable invariants and risks:
- Sysfs itself does not generally serialize object lifetime; owners must avoid races, except for symlink target dereference protection through `sysfs_symlink_target_lock`.
