# File Research: sources/os/linux/linux-stable/fs/sysfs/sysfs.h

Purpose: Internal sysfs header shared by sysfs implementation files.

Key responsibilities:
- Declares `sysfs_root_kn`.
- Declares `sysfs_symlink_target_lock`.
- Declares `sysfs_warn_dup()`.
- Declares internal file creation helpers for regular and binary attributes with explicit mode, ownership, and namespace.
- Declares `sysfs_create_link_sd()`.

Important interactions:
- Bridges mount, dir, file, group, and symlink implementation files.
- Includes public `<linux/sysfs.h>` while keeping kernfs-oriented internals private to `fs/sysfs`.

Notable invariants and risks:
- This is not a public API header; exported user-facing sysfs APIs live elsewhere.
