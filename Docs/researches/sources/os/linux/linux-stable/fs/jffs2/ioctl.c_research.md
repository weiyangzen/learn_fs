# File Research: sources/os/linux/linux-stable/fs/jffs2/ioctl.c

## Role

Placeholder ioctl implementation for JFFS2 files and directories.

## Key Function

- `jffs2_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)` always returns `-ENOTTY`.

## Research Notes

The comment notes a future intent for `lsattr.jffs2`/`chattr.jffs2` support, including compression-related attributes. In this version, JFFS2 exposes no private ioctl commands through this file.
