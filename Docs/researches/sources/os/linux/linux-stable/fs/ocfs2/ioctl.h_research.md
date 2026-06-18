# File Research: sources/os/linux/linux-stable/fs/ocfs2/ioctl.h

Purpose: declares OCFS2 file attribute and ioctl entry points used by the VFS file/inode operation tables.

Read coverage: complete file read, 20 lines.

Declared APIs:
- `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` implement Linux fileattr operations for OCFS2 inode flags.
- `ocfs2_ioctl()` is the native ioctl dispatcher.
- `ocfs2_compat_ioctl()` is the compat dispatcher for 32-bit userspace on 64-bit kernels.

Important dependencies:
- Uses VFS `dentry`, `mnt_idmap`, `file_kattr`, and `file` types; implementation is in `ioctl.c`.

Risk and edge cases:
- The header intentionally exposes only the ioctl surface, leaving command-specific structures in OCFS2 UAPI/internal headers.
