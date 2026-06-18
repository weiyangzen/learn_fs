# File Research: sources/os/linux/linux/fs/jffs2/ioctl.c

This file contains the JFFS2 ioctl entry point. `jffs2_ioctl()` currently returns `-ENOTTY` for all commands.

The comment notes a planned future interface for `lsattr.jffs2` and `chattr.jffs2`, including compression-related support, but no command decoding exists here.

Key dependencies: VFS file operation dispatch from `file.c` and `dir.c`, which both wire `.unlocked_ioctl = jffs2_ioctl`.
