# File Research: sources/os/linux/linux/fs/sysfs/symlink.c

Purpose: sysfs symlink creation, deletion, removal, and rename helpers.

Key APIs:
- `sysfs_create_link_sd()` creates a link under a kernfs node.
- `sysfs_create_link()` and `sysfs_create_link_nowarn()` create links under kobject directories; both exported.
- `sysfs_delete_link()` removes namespace-aware symlinks when target kobject is known.
- `sysfs_remove_link()` removes a symlink by name; exported.
- `sysfs_rename_link_ns()` validates symlink target and renames with a new namespace; exported.

Concurrency and correctness:
- Link creation and namespace lookup synchronize against target directory removal with `sysfs_symlink_target_lock`.
- Target kernfs node is temporarily referenced before link creation.
- Rename validates that the found kernfs node is a link and points to the expected target kobject.
