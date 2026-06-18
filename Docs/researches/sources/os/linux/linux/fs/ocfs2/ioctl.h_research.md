# File Research: sources/os/linux/linux/fs/ocfs2/ioctl.h

`ioctl.h` is the public internal prototype header for OCFS2 ioctl and file attribute handling.

It declares:
- `ocfs2_fileattr_get()`
- `ocfs2_fileattr_set()`
- `ocfs2_ioctl()`
- `ocfs2_compat_ioctl()`

The header connects OCFS2 inode/file operation tables to the implementation in `ioctl.c`. It contains no policy beyond include guards and function prototypes.
