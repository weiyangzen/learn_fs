# File Research: sources/os/linux/linux-stable/fs/vboxsf/dir.c

Implements vboxsf directory file operations, dentry validation, and directory inode operations. Directory open creates a host directory handle with `vboxsf_create_at_dentry()`, reads all directory entries from the host into `vboxsf_dir_info`, then closes the host handle and stores the buffered entries in `file->private_data`.

`vboxsf_dir_iterate()` emits buffered entries using `dir_emit()`, synthesizing inode numbers from directory position and mapping VirtualBox mode bits to Linux `d_type`. It supports optional NLS conversion via `vboxsf_nlscpy()` and skips entries that fail conversion.

Lookup and dentry revalidation call `vboxsf_stat_dentry()` and create/reinitialize Linux inodes through `vboxsf_new_inode()` and `vboxsf_init_inode()`. Create, mkdir, atomic open, unlink/rmdir, rename, and symlink translate VFS operations into host protocol calls, then mark parent inodes for restat when host metadata may have changed.

Important behavior: the driver trusts but bounds-checks variable-sized host directory records, rejects RCU lookup revalidation, does not support rename flags, and returns `-EPERM` for unsupported host symlink creation reported as read-only.
