# File Research: sources/os/linux/linux/fs/sysfs/dir.c

Purpose: sysfs directory creation, removal, rename/move, duplicate warnings, and mount-point directory helpers.

Key APIs:
- `sysfs_create_dir_ns(kobj, ns)` creates a kernfs directory for a kobject with namespace tag and ownership from `kobject_get_ownership`.
- `sysfs_remove_dir(kobj)` disassociates `kobj->sd` and removes the kernfs directory.
- `sysfs_rename_dir_ns()` and `sysfs_move_dir_ns()` wrap kernfs namespace-aware rename/move.
- `sysfs_create_mount_point()` and `sysfs_remove_mount_point()` create/remove always-empty directories; both are GPL exported.
- `sysfs_warn_dup()` logs duplicate filename errors and dumps stack.

Concurrency and correctness:
- Defines `sysfs_symlink_target_lock`, used to protect `kobj->sd` against races between directory removal and symlink operations.
- `sysfs_remove_dir()` clears `kobj->sd` under that spinlock before kernfs removal.
- Duplicate creation paths warn on `-EEXIST`.

Dependencies:
- kernfs directory primitives and kobject ownership/name APIs.
