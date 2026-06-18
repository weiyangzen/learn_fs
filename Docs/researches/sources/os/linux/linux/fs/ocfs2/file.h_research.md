# File Research: sources/os/linux/linux/fs/ocfs2/file.h

Public header for OCFS2 file and inode operation helpers.

Exports operation tables:
- `ocfs2_fops`, `ocfs2_dops`
- `ocfs2_fops_no_plocks`, `ocfs2_dops_no_plocks`
- `ocfs2_file_iops`, `ocfs2_special_file_iops`

Defines:
- `struct ocfs2_file_private`: directory cookie, backing `struct file`, mutex, and per-file flock lock resource.

Declares helpers for:
- Extent allocation into an inode: `ocfs2_add_inode_data()`.
- Size updates: `ocfs2_set_inode_size()`, `ocfs2_simple_size_update()`.
- Truncate/extend: `ocfs2_truncate_file()`, `ocfs2_extend_no_holes()`, `ocfs2_zero_extend()`.
- VFS inode ops: `ocfs2_setattr()`, `ocfs2_getattr()`, `ocfs2_permission()`.
- Atime policy/update: `ocfs2_should_update_atime()`, `ocfs2_update_inode_atime()`.
- Reservation/hole-punch ioctls: `ocfs2_change_file_space()`.
- Refcount and range removal helpers: `ocfs2_check_range_for_refcount()`, `ocfs2_remove_inode_range()`.

Role:
- Shared by address-space, ioctl, inode, and other OCFS2 modules that need file-size/allocation behavior without owning VFS operation tables directly.
