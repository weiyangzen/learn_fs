# File Research: sources/os/linux/linux/fs/xfs/xfs_handle.h

Declares XFS handle, attribute-by-handle, and parent-pointer ioctl helpers.

Key contents:
- Attribute list and multi-attribute operations by handle.
- Handle creation/open/readlink helpers.
- Single attrmulti operation helper and attr list helper.
- Userspace handle-to-dentry decoder.
- GETPARENTS entry points for current file and by handle.

This header exposes privileged handle-based functionality used by XFS ioctl dispatch.
