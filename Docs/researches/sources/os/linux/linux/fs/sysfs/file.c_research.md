# File Research: sources/os/linux/linux/fs/sysfs/file.c

Purpose: sysfs regular and binary attribute file implementation over kernfs.

Key APIs:
- Attribute creation/removal: `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_remove_file_ns`, `sysfs_remove_files`, `sysfs_add_file_to_group`, `sysfs_remove_file_from_group`.
- Binary attributes: `sysfs_create_bin_file`, `sysfs_remove_bin_file`, `sysfs_bin_attr_simple_read`.
- Runtime updates: `sysfs_notify`, `sysfs_chmod_file`, `sysfs_break_active_protection`, `sysfs_unbreak_active_protection`.
- Ownership changes: `sysfs_link_change_owner`, `sysfs_file_change_owner`, `sysfs_change_owner`.
- Output helpers: `sysfs_emit`, `sysfs_emit_at`.

Implementation notes:
- Maps `sysfs_ops->show/store` to kernfs seq/read/write callbacks, with preallocated-buffer variants for `SYSFS_PREALLOC`.
- Binary attributes support read, write, mmap, custom llseek, open-time mapping override, and size bounds.
- Attribute mode is masked to sysfs-supported permissions during group creation paths.
- `sysfs_emit*` validate PAGE_SIZE-aligned sysfs buffers and use `vscnprintf`.

Concurrency and correctness:
- `sysfs_file_ops()` requires active kernfs protection and asserts lockdep when `KERNFS_LOCKDEP` is set.
- Active protection break/unbreak is provided for self-deleting sysfs attributes and pins both kobject and kernfs node.
- Ownership change helpers validate object presence in sysfs and symlink target identity before mutation.
