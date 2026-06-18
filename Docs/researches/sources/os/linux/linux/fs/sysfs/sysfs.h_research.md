# File Research: sources/os/linux/linux/fs/sysfs/sysfs.h

Purpose: Internal sysfs header shared by sysfs implementation files.

Contents:
- Includes public `<linux/sysfs.h>`.
- Declares internal `sysfs_root_kn`.
- Declares `sysfs_symlink_target_lock`.
- Declares `sysfs_warn_dup`.
- Declares file creation helpers `sysfs_add_file_mode_ns` and `sysfs_add_bin_file_mode_ns`.
- Declares symlink helper `sysfs_create_link_sd`.

Role:
- Keeps kernfs-level internals private to `fs/sysfs` while allowing dir/file/group/symlink/mount code to cooperate.
